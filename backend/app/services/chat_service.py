import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.analysis.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logger import logger
from app.database.mongodb import get_database
from app.rag.clarification_guard import ClarificationGuard
from app.rag.intent_classifier import IntentClassifier, IntentType
from app.rag.retriever import PatientRAGRetriever

# Fallback memory store if MongoDB is down
in_memory_chat_history: Dict[str, List[Dict[str, Any]]] = {}


class ChatService:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.retriever = PatientRAGRetriever()
        self.clarification_guard = ClarificationGuard()
        self.groq_client = GroqClient()

    async def process_chat_message(
        self,
        patient_id: str,
        message: str,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        message_id = str(uuid.uuid4())

        # 1. Intent Classification
        classification = self.intent_classifier.classify(message)
        intent = classification["intent"]

        # 2. Retrieve Patient-Scoped Context & Citations
        retrieved = await self.retriever.retrieve_context(patient_id=patient_id, query=message, analysis_id=analysis_id)
        previous_report_count = retrieved.get("previous_report_count", 0)

        # 3. Clarification Safety Guardrail Check
        guard_result = self.clarification_guard.evaluate_history_sufficiency(
            intent=intent,
            previous_report_count=previous_report_count,
            patient_id=patient_id
        )

        if not guard_result["sufficient"]:
            response_text = guard_result["clarification_message"]
            chat_record = {
                "message_id": message_id,
                "patient_id": patient_id,
                "analysis_id": analysis_id,
                "user_message": message,
                "bot_response": response_text,
                "intent": intent,
                "citations": retrieved.get("citations", []),
                "clarification_triggered": True,
                "created_at": now
            }
            await self._save_chat_record(patient_id, chat_record)
            return chat_record

        # 4. Generate Grounded LLM Answer
        response_text = await self._generate_response(
            message=message,
            intent=intent,
            retrieved=retrieved
        )

        chat_record = {
            "message_id": message_id,
            "patient_id": patient_id,
            "analysis_id": analysis_id,
            "user_message": message,
            "bot_response": response_text,
            "intent": intent,
            "citations": retrieved.get("citations", []),
            "clarification_triggered": False,
            "created_at": now
        }

        await self._save_chat_record(patient_id, chat_record)
        return chat_record

    async def _generate_response(self, message: str, intent: str, retrieved: Dict[str, Any]) -> str:
        patient_name = retrieved.get("patient_name") or "the patient"
        comparison_context = retrieved.get("comparison_context") or {}
        parsed_json = retrieved.get("parsed_json") or {}
        comparisons = comparison_context.get("comparisons") or []

        # Attempt Groq LLM Generation first if enabled
        if self.groq_client.enabled and settings.LLM_PROVIDER.lower() == "groq":
            prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are an AI Medical Assistant. Use ONLY the provided structured patient facts and historical trends. "
                        "Do not diagnose diseases, do not invent unmentioned lab values, and provide patient-friendly explanations."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Patient Name: {patient_name}\n"
                        f"Query Intent: {intent}\n"
                        f"User Question: {message}\n"
                        f"Current Medical JSON Facts: {parsed_json}\n"
                        f"Historical Lab Comparisons: {comparisons}\n"
                        f"Relevant Vector Knowledge: {[v.get('text') for v in retrieved.get('vector_results', [])]}\n\n"
                        "Provide a concise, grounded, patient-friendly answer."
                    )
                }
            ]
            try:
                llm_ans = await self.groq_client.chat_completion(prompt)
                if llm_ans and len(llm_ans.strip()) > 10:
                    return llm_ans
            except Exception as exc:
                logger.warning(f"Groq chat generation failed, using deterministic fallback: {exc}")

        # Deterministic Grounded Fallback Generation
        return self._build_deterministic_chat_response(
            intent=intent,
            message=message,
            patient_name=patient_name,
            comparisons=comparisons,
            parsed_json=parsed_json,
            vector_results=retrieved.get("vector_results", [])
        )

    def _build_deterministic_chat_response(
        self,
        intent: str,
        message: str,
        patient_name: str,
        comparisons: List[Dict[str, Any]],
        parsed_json: Dict[str, Any],
        vector_results: List[Dict[str, Any]] = None
    ) -> str:
        vector_results = vector_results or []
        kb_excerpts = [v.get("text") for v in vector_results if v.get("text")]

        if intent == IntentType.REPORT_HISTORY_QUERY:
            if not comparisons:
                return f"I analyzed {patient_name}'s current report, but there are no prior reports with comparable lab values to determine a historical trend."
            lines = [f"Based on historical reports for {patient_name}:"]
            for comp in comparisons:
                test = comp.get("test_name", "Test")
                curr = comp.get("current_value")
                prev = comp.get("previous_value")
                status = comp.get("finding_status", "").lower().replace("_", " ")
                if prev is not None and curr is not None:
                    lines.append(f"• {test} changed from {prev:g} to {curr:g} ({status}).")
            lines.append("Please discuss these longitudinal trends with your primary physician.")
            return "\n".join(lines)

        if intent == IntentType.REPORT_FACT_QUERY:
            labs = parsed_json.get("lab_results") or parsed_json.get("lab_facts") or []
            if labs:
                facts_str = ", ".join([f"{l.get('test_name')}: {l.get('value')} {l.get('unit') or ''}" for l in labs[:5]])
                res = f"Here are the current lab findings for {patient_name}: {facts_str}."
                if kb_excerpts:
                    res += f"\n\nFAISS Clinical Reference Context: {kb_excerpts[0]}"
                return res
            if kb_excerpts:
                return f"Based on indexed FAISS records for {patient_name}: {kb_excerpts[0]}"
            return f"No specific lab values were found in {patient_name}'s current parsed report."

        if intent == IntentType.EXPLANATION_QUERY:
            if kb_excerpts:
                return f"According to clinical reference knowledge: {kb_excerpts[0]}"

        if intent == IntentType.REANALYSIS_REQUEST:
            return f"Re-analysis request received. I have evaluated {patient_name}'s current report against all accumulated historical workspaces and FAISS vector index."

        if kb_excerpts:
            return f"Based on {patient_name}'s indexed medical records (FAISS match score > 0.3): {kb_excerpts[0]}"

        return f"Based on {patient_name}'s medical records, your findings have been analyzed using grounded clinical rules. Please review the detailed comparison view or consult your healthcare provider for clinical guidance."


    async def get_chat_history(self, patient_id: str) -> List[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                cursor = db.chat_history.find({"patient_id": patient_id}).sort("created_at", 1)
                history = []
                async for doc in cursor:
                    doc["_id"] = str(doc["_id"])
                    history.append(doc)
                return history
            except Exception as exc:
                logger.warning(f"Failed to fetch chat history from Mongo: {exc}")

        return in_memory_chat_history.get(patient_id, [])

    async def clear_chat_history(self, patient_id: str) -> bool:
        db = get_database()
        if db is not None:
            try:
                await db.chat_history.delete_many({"patient_id": patient_id})
            except Exception as exc:
                logger.warning(f"Failed to delete chat history from Mongo: {exc}")

        in_memory_chat_history[patient_id] = []
        return True

    async def _save_chat_record(self, patient_id: str, record: Dict[str, Any]) -> None:
        db = get_database()
        if db is not None:
            try:
                await db.chat_history.insert_one(dict(record))
                return
            except Exception as exc:
                logger.warning(f"Failed to save chat record to Mongo: {exc}")

        if patient_id not in in_memory_chat_history:
            in_memory_chat_history[patient_id] = []
        in_memory_chat_history[patient_id].append(record)

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
                "response": response_text,
                "intent": intent,
                "classified_intent": intent,
                "citations": retrieved.get("citations", []),
                "clarification_triggered": True,
                "created_at": now
            }
            await self._save_chat_record(patient_id, chat_record)
            return chat_record

        # 4. Generate Grounded LLM Answer
        try:
            response_text = await self._generate_response(
                message=message,
                intent=intent,
                retrieved=retrieved
            )
        except Exception as exc:
            logger.warning(f"Error in _generate_response: {exc}")
            response_text = self._build_deterministic_chat_response(
                intent=intent,
                message=message,
                patient_name=retrieved.get("patient_name") or "the patient",
                comparisons=(retrieved.get("comparison_context") or {}).get("comparisons") or [],
                parsed_json=retrieved.get("parsed_json") or {},
                vector_results=retrieved.get("vector_results") or []
            )

        if not response_text or not isinstance(response_text, str):
            response_text = f"Based on the medical reports available in the system for {retrieved.get('patient_name') or 'the patient'}, no specific information could be retrieved for this query. Please consult your physician."

        chat_record = {
            "message_id": message_id,
            "patient_id": patient_id,
            "analysis_id": analysis_id,
            "user_message": message,
            "bot_response": response_text,
            "response": response_text,
            "intent": intent,
            "classified_intent": intent,
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
        vector_results: List[Dict[str, Any]] = None,
        patient_id: Optional[str] = None,
    ) -> str:
        vector_results = vector_results or []
        kb_excerpts = [v.get("text") for v in vector_results if v.get("text")]

        has_medical_data = bool(parsed_json or comparisons or any((v.get("metadata") or {}).get("patient_id") for v in vector_results))

        if not has_medical_data:
            if intent in {IntentType.REPORT_FACT_QUERY, IntentType.REPORT_HISTORY_QUERY}:
                return f"There are no recorded medical reports or lab measurements for {patient_name} in the system yet. Please upload a medical report first to analyze and query clinical values."

        if intent == IntentType.REPORT_HISTORY_QUERY:
            if not comparisons:
                return f"I analyzed {patient_name}'s current records, but there are no prior historical reports with comparable lab values to determine a trend."
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
                return res
            # Check if any patient-specific vector chunk exists
            patient_chunks = [v.get("text") for v in vector_results if (v.get("metadata") or {}).get("patient_id")]
            if patient_chunks:
                return f"Based on indexed records for {patient_name}: {patient_chunks[0]}"
            return f"No specific laboratory measurement for this parameter was found in {patient_name}'s medical records."

        if intent == IntentType.EXPLANATION_QUERY:
            if kb_excerpts:
                return f"According to clinical reference knowledge: {kb_excerpts[0]}"

        if intent == IntentType.REANALYSIS_REQUEST:
            return f"Re-analysis request received. Evaluated {patient_name}'s reports against available longitudinal history and clinical knowledge."

        patient_chunks = [v.get("text") for v in vector_results if (v.get("metadata") or {}).get("patient_id")]
        if patient_chunks:
            return f"Based on {patient_name}'s indexed medical records: {patient_chunks[0]}"
        elif kb_excerpts:
            return f"According to clinical guidelines: {kb_excerpts[0]}"

        return f"Based on {patient_name}'s medical records, no specific evidence was found for this query. Please consult your physician for clinical advice."


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

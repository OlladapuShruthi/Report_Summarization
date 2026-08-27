import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from app.rag.intent_classifier import IntentClassifier, IntentType
from app.embeddings.vector_store import PatientVectorStore
from app.rag.clarification_guard import ClarificationGuard

client = TestClient(app)


def test_intent_classifier():
    classifier = IntentClassifier()

    history_res = classifier.classify("Is my hemoglobin improving compared to previous reports?")
    assert history_res["intent"] == IntentType.REPORT_HISTORY_QUERY

    fact_res = classifier.classify("What is my current RBC count?")
    assert fact_res["intent"] == IntentType.REPORT_FACT_QUERY

    explanation_res = classifier.classify("What does MCV mean?")
    assert explanation_res["intent"] == IntentType.EXPLANATION_QUERY

    reanalysis_res = classifier.classify("Compare all my reports again and re-analyze")
    assert reanalysis_res["intent"] == IntentType.REANALYSIS_REQUEST


def test_vector_store_patient_isolation():
    store = PatientVectorStore()
    store.add_document("doc_p1", "Patient A hemoglobin level is 10.2", {"patient_id": "P001", "source_type": "report"})
    store.add_document("doc_p2", "Patient B thyroid TSH level is 2.5", {"patient_id": "P002", "source_type": "report"})

    # Search scoped to P001 MUST NOT return doc_p2!
    results_p1 = store.search("hemoglobin thyroid", patient_id="P001")
    doc_ids_p1 = [r["doc_id"] for r in results_p1]

    assert "doc_p1" in doc_ids_p1
    assert "doc_p2" not in doc_ids_p1


def test_clarification_guard_triggers_when_history_missing():
    eval_res = ClarificationGuard.evaluate_history_sufficiency(
        intent=IntentType.REPORT_HISTORY_QUERY,
        previous_report_count=0,
        patient_id="P001"
    )

    assert eval_res["sufficient"] is False
    assert eval_res["reason"] == "MISSING_HISTORICAL_REPORTS"
    assert "I only have your current medical report available" in eval_res["clarification_message"]


def test_chat_api_endpoints():
    # 1. Create Patient Profile
    patient_res = client.post("/api/v1/patients", json={
        "display_name": "Chat Test Patient",
        "sex": "MALE"
    })
    assert patient_res.status_code == 200
    patient_id = patient_res.json()["data"]["patient_id"]

    # 2. Send Chat Message
    chat_res = client.post("/api/v1/chat/message", json={
        "patient_id": patient_id,
        "message": "What are my current lab findings?"
    })
    assert chat_res.status_code == 200
    data = chat_res.json()["data"]
    assert data["patient_id"] == patient_id
    assert "bot_response" in data
    assert "citations" in data

    # 3. Retrieve Chat History
    history_res = client.get(f"/api/v1/chat/history/{patient_id}")
    assert history_res.status_code == 200
    history_data = history_res.json()["data"]
    assert len(history_data) >= 1
    assert history_data[0]["user_message"] == "What are my current lab findings?"

import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from app.embeddings.vector_store import PatientVectorStore, vector_store
from app.rag.retriever import PatientRAGRetriever
from app.services.chat_service import ChatService

client = TestClient(app)


def test_faiss_indexing_and_isolation():
    store = PatientVectorStore()
    
    # 1. Index Report Chunks for Patient 101
    store.add_document(
        doc_id="p101_hb",
        text="Patient 101 Hemoglobin level is 9.5 g/dL indicating moderate anemia.",
        metadata={"patient_id": "P101", "source_type": "patient_lab_fact", "title": "Hemoglobin Fact"}
    )
    
    # 2. Index Report Chunks for Patient 202
    store.add_document(
        doc_id="p202_tsh",
        text="Patient 202 Thyroid TSH level is 7.2 uIU/mL indicating hypothyroidism.",
        metadata={"patient_id": "P202", "source_type": "patient_lab_fact", "title": "TSH Fact"}
    )

    # 3. Query for Patient 101 MUST NOT contain Patient 202 records!
    p101_results = store.search("anemia thyroid hemoglobin", patient_id="P101", top_k=5)
    p101_doc_ids = [r["doc_id"] for r in p101_results]
    
    assert "p101_hb" in p101_doc_ids
    assert "p202_tsh" not in p101_doc_ids
    
    # 4. Clinical reference knowledge (patient_id=None) SHOULD be accessible
    who_res = store.search("WHO Hemoglobin normal range", patient_id="P101", top_k=5)
    who_doc_ids = [r["doc_id"] for r in who_res]
    assert "kb_who_hb" in who_doc_ids


def test_dynamic_report_chunk_indexing():
    store = PatientVectorStore()
    sample_parsed_json = {
        "patient_metadata": {
            "name": "Jane Doe",
            "age": 45,
            "sex": "FEMALE",
            "report_date": "2026-08-15"
        },
        "lab_results": [
            {"test_name": "Hemoglobin", "value": 10.5, "unit": "g/dL", "reference_range": "12.0 - 15.5", "finding_status": "LOW"},
            {"test_name": "Platelets", "value": 250, "unit": "K/uL", "reference_range": "150 - 450", "finding_status": "NORMAL"}
        ]
    }
    
    chunks_count = store.index_report(patient_id="P555", analysis_id="sess_555", parsed_json=sample_parsed_json)
    assert chunks_count >= 3
    
    search_res = store.search("Platelets count normal range", patient_id="P555")
    assert len(search_res) > 0
    matched_doc_ids = [r["doc_id"] for r in search_res]
    assert any("sess_555_lab" in doc_id for doc_id in matched_doc_ids)


def test_faiss_records_survive_store_reload(tmp_path):
    first_store = PatientVectorStore(storage_dir=str(tmp_path))
    first_store.add_document(
        doc_id="persistent_hb",
        text="Patient PERSISTENT Hemoglobin is 10.2 g/dL.",
        metadata={"patient_id": "PERSISTENT", "source_type": "patient_lab_fact"},
    )

    reloaded_store = PatientVectorStore(storage_dir=str(tmp_path))
    results = reloaded_store.search("Hemoglobin", patient_id="PERSISTENT")

    assert any(result["doc_id"] == "persistent_hb" for result in results)


@pytest.mark.asyncio
async def test_rag_retriever_with_faiss_citations():
    retriever = PatientRAGRetriever()
    
    # Index test chunk into global singleton vector store
    vector_store.add_document(
        doc_id="test_faiss_cit",
        text="Clinical guidance on Low Hemoglobin: Iron supplementation and dietary adjustment.",
        metadata={"source_type": "clinical_knowledge", "title": "Iron Deficiency Guidelines", "patient_id": None}
    )

    ctx = await retriever.retrieve_context(patient_id="P999", query="What should I do for low hemoglobin?")
    assert "vector_results" in ctx
    assert "citations" in ctx
    
    citation_types = [c["type"] for c in ctx["citations"]]
    assert any("FAISS" in c_type for c_type in citation_types)


def test_end_to_end_chat_api_with_faiss():
    # 1. Create Patient
    p_res = client.post("/api/v1/patients", json={"display_name": "FAISS Test Patient", "sex": "FEMALE"})
    assert p_res.status_code == 200
    p_id = p_res.json()["data"]["patient_id"]
    
    # 2. Send Message to Chat API
    chat_res = client.post("/api/v1/chat/message", json={
        "patient_id": p_id,
        "message": "What is the normal reference range for Hemoglobin?"
    })
    assert chat_res.status_code == 200
    data = chat_res.json()["data"]
    
    assert data["patient_id"] == p_id
    assert "bot_response" in data
    assert len(data["bot_response"]) > 10
    assert "citations" in data
    assert any("FAISS" in c.get("type", "") for c in data["citations"])

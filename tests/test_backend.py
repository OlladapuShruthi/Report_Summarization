import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert "data" in res_data

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["status"] == "healthy"
    assert "database" in res_data["data"]

def test_create_and_upload_analysis_workspace():
    # 1. Create Workspace
    create_res = client.post("/api/v1/analysis/create", data={"title": "Test Clinical Session"})
    assert create_res.status_code == 200
    create_body = create_res.json()
    assert create_body["success"] is True
    analysis_id = create_body["data"]["analysis_id"]
    assert create_body["data"]["status"] == "created"

    # 2. Upload Report to Workspace
    file_content = b"Sample Clinical PDF Report - Hemoglobin 14.5 g/dL Normal."
    files = {"file": ("patient_report.pdf", file_content, "application/pdf")}
    
    upload_res = client.post(f"/api/v1/analysis/{analysis_id}/upload", files=files)
    assert upload_res.status_code == 200
    upload_body = upload_res.json()
    assert upload_body["success"] is True
    assert upload_body["data"]["status"] == "uploaded"
    assert upload_body["data"]["document_info"]["original_filename"] == "patient_report.pdf"

    # 3. Get Workspace detail
    get_res = client.get(f"/api/v1/analysis/{analysis_id}")
    assert get_res.status_code == 200
    get_body = get_res.json()
    assert get_body["success"] is True
    assert get_body["data"]["analysis_id"] == analysis_id

def test_parse_uploaded_analysis_workspace():
    create_res = client.post("/api/v1/analysis/create", data={"title": "Parse Test Session"})
    assert create_res.status_code == 200
    analysis_id = create_res.json()["data"]["analysis_id"]

    file_content = (
        b"Complete Blood Count Report\n"
        b"Hemoglobin 10.2 g/dL 13.5-17.5\n"
        b"WBC 6200 cells/uL 4000-11000\n"
        b"Platelets 250000 cells/uL 150000-450000\n"
    )
    files = {"file": ("cbc_report.pdf", file_content, "application/pdf")}
    upload_res = client.post(f"/api/v1/analysis/{analysis_id}/upload", files=files)
    assert upload_res.status_code == 200

    parse_res = client.post(f"/api/v1/analysis/{analysis_id}/parse")
    assert parse_res.status_code == 200
    body = parse_res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "parsed"
    assert data["parsed_json"]["schema_version"] == "1.0"
    assert data["parsed_json"]["report_type"] == "LAB_REPORT_CBC"
    assert len(data["parsed_json"]["lab_results"]) >= 3
    assert data["cleaned_text"]

def test_quick_start_analysis():
    file_content = b"Quick Start Report Content."
    files = {"file": ("quick_report.pdf", file_content, "application/pdf")}
    
    res = client.post("/api/v1/analysis/quick-start", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["status"] == "uploaded"
    assert "analysis_id" in body["data"]

def test_list_analysis_sessions():
    res = client.get("/api/v1/analysis/sessions")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)

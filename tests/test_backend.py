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

def test_patient_profiles_scope_analysis_workspaces():
    patient_res = client.post("/api/v1/patients", json={"display_name": "Rahul Sharma", "sex": "MALE"})
    assert patient_res.status_code == 200
    patient = patient_res.json()["data"]

    create_res = client.post("/api/v1/analysis/create", data={"patient_id": patient["patient_id"]})
    assert create_res.json()["success"] is True
    assert create_res.json()["data"]["patient_id"] == patient["patient_id"]

    sessions_res = client.get("/api/v1/analysis/sessions", params={"patient_id": patient["patient_id"]})
    assert sessions_res.json()["success"] is True
    assert all(item["patient_id"] == patient["patient_id"] for item in sessions_res.json()["data"])

    unknown_patient_res = client.post("/api/v1/analysis/create", data={"patient_id": "not-a-patient"})
    assert unknown_patient_res.json()["success"] is False

def _create_test_patient(name="Test Patient"):
    res = client.post("/api/v1/patients", json={"display_name": name})
    return res.json()["data"]["patient_id"]

def test_analysis_create_rejects_missing_patient_id():
    res = client.post("/api/v1/analysis/create", data={"title": "Orphan Analysis"})
    assert res.status_code == 400
    assert res.json()["success"] is False
    assert res.json()["error"]["code"] == "PATIENT_ID_REQUIRED"

def test_create_and_upload_analysis_workspace():
    # 1. Create Patient and Workspace
    patient_id = _create_test_patient("Workspace Patient")
    create_res = client.post("/api/v1/analysis/create", data={"title": "Test Clinical Session", "patient_id": patient_id})
    assert create_res.status_code == 200
    create_body = create_res.json()
    assert create_body["success"] is True
    analysis_id = create_body["data"]["analysis_id"]
    assert create_body["data"]["patient_id"] == patient_id
    assert create_body["data"]["status"] == "created"

    # 2. Upload Report to Workspace
    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "documents", "uploads",
        "33b70989-729d-4bb6-a24a-ccbd31183833_Sample_CBC_Lab_Report.pdf",
    )
    with open(sample_path, "rb") as report_file:
        upload_res = client.post(
            f"/api/v1/analysis/{analysis_id}/upload",
            files={"file": ("patient_report.pdf", report_file, "application/pdf")},
        )
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


def test_follow_up_upload_creates_linked_patient_scoped_session():
    patient_res = client.post("/api/v1/patients", json={"display_name": "Follow-up Patient"})
    patient_id = patient_res.json()["data"]["patient_id"]
    create_res = client.post(
        "/api/v1/analysis/create",
        data={"patient_id": patient_id, "title": "Initial Report"},
    )
    original_id = create_res.json()["data"]["analysis_id"]
    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "documents", "uploads",
        "33b70989-729d-4bb6-a24a-ccbd31183833_Sample_CBC_Lab_Report.pdf",
    )

    with open(sample_path, "rb") as report_file:
        response = client.post(
            f"/api/v1/analysis/{original_id}/follow-up",
            files={"file": ("follow_up.pdf", report_file, "application/pdf")},
        )

    assert response.status_code == 200
    follow_up = response.json()["data"]
    assert follow_up["analysis_id"] != original_id
    assert follow_up["patient_id"] == patient_id
    assert follow_up["follow_up_for_analysis_id"] == original_id
    assert follow_up["status"] == "uploaded"

def test_parse_uploaded_analysis_workspace():
    patient_id = _create_test_patient("Parse Patient")
    create_res = client.post("/api/v1/analysis/create", data={"title": "Parse Test Session", "patient_id": patient_id})
    assert create_res.status_code == 200
    analysis_id = create_res.json()["data"]["analysis_id"]

    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "documents", "uploads",
        "33b70989-729d-4bb6-a24a-ccbd31183833_Sample_CBC_Lab_Report.pdf",
    )
    with open(sample_path, "rb") as report_file:
        upload_res = client.post(
            f"/api/v1/analysis/{analysis_id}/upload",
            files={"file": ("cbc_report.pdf", report_file, "application/pdf")},
        )
    assert upload_res.status_code == 200

    parse_res = client.post(f"/api/v1/analysis/{analysis_id}/parse")
    assert parse_res.status_code == 200
    body = parse_res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "parsed"
    assert data["parsed_json"]["schema_version"] == "1.0"
    assert data["parsed_json"]["report_type"] == "LAB_REPORT_CBC"
    assert data["parsed_json"]["patient_metadata"]["name"] == "Rahul Sharma"
    assert data["parsed_json"]["lab_results"][0]["category"] == "Hematology"
    assert data["parsed_json"]["lab_results"][0]["is_outside_reference"] is True
    assert len(data["parsed_json"]["lab_results"]) >= 3
    assert data["cleaned_text"]


def test_analyze_parsed_analysis_workspace():
    patient_id = _create_test_patient("Analyze Patient")
    create_res = client.post("/api/v1/analysis/create", data={"title": "Analyze Test Session", "patient_id": patient_id})
    assert create_res.status_code == 200
    analysis_id = create_res.json()["data"]["analysis_id"]

    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "documents", "uploads",
        "33b70989-729d-4bb6-a24a-ccbd31183833_Sample_CBC_Lab_Report.pdf",
    )
    with open(sample_path, "rb") as report_file:
        upload_res = client.post(
            f"/api/v1/analysis/{analysis_id}/upload",
            files={"file": ("cbc_report.pdf", report_file, "application/pdf")},
        )
    assert upload_res.status_code == 200

    parse_res = client.post(f"/api/v1/analysis/{analysis_id}/parse")
    assert parse_res.status_code == 200

    analyze_res = client.post(f"/api/v1/analysis/{analysis_id}/analyze")
    assert analyze_res.status_code == 200
    body = analyze_res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "completed"
    assert data["summary_report"]
    assert data["validation_status"]["passed"] is True
    assert data["execution_log"]


def test_uncertain_real_report_requires_review_before_analysis():
    patient_id = _create_test_patient("Cardio Patient")
    create_res = client.post("/api/v1/analysis/create", data={"title": "Cardio Review Session", "patient_id": patient_id})
    analysis_id = create_res.json()["data"]["analysis_id"]
    sample_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "documents",
        "uploads",
        "91f29440-69b5-4991-ab9e-944375e791d7_OMC Report Sample - Cardio.pdf",
    )

    with open(sample_path, "rb") as report_file:
        upload_res = client.post(
            f"/api/v1/analysis/{analysis_id}/upload",
            files={"file": ("cardio.pdf", report_file, "application/pdf")},
        )
    assert upload_res.status_code == 200

    parse_res = client.post(f"/api/v1/analysis/{analysis_id}/parse")
    assert parse_res.status_code == 200
    parsed = parse_res.json()["data"]
    assert parsed["status"] == "needs_review"
    assert parsed["review_required"] is True
    assert parsed["parsed_json"]["lab_results"] == []

    analyze_res = client.post(f"/api/v1/analysis/{analysis_id}/analyze")
    body = analyze_res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ANALYSIS_REVIEW_REQUIRED"

    questions_res = client.get(f"/api/v1/analysis/{analysis_id}/review-questions")
    assert questions_res.status_code == 200
    questions = questions_res.json()["data"]["questions"]
    assert questions
    assert questions[0]["status"] == "pending"
    assert questions_res.json()["data"]["review_policy"]["analysis_allowed"] is False

    answer_res = None
    for question in questions:
        answer_res = client.post(
            f"/api/v1/analysis/{analysis_id}/review-questions/{question['question_id']}/answer",
            json={
                "action": "confirm",
                "response": "This is a clinical narrative report.",
                "finding_id": "hemoglobin|g/dl",
            },
        )
    assert answer_res.status_code == 200
    answer = answer_res.json()["data"]
    assert answer["status"] == "answered"
    assert answer["evidence_type"] == "PATIENT_REPORTED"
    assert answer["finding_id"] == "hemoglobin|g/dl"

    policy_res = client.get(f"/api/v1/analysis/{analysis_id}/review-questions")
    assert policy_res.json()["data"]["review_policy"]["status"] == "acknowledged"
    assert policy_res.json()["data"]["review_policy"]["analysis_allowed"] is False


def test_analysis_progress_endpoint_returns_stage_information():
    patient_id = _create_test_patient("Progress Patient")
    create_res = client.post("/api/v1/analysis/create", data={"title": "Progress Test Session", "patient_id": patient_id})
    assert create_res.status_code == 200
    analysis_id = create_res.json()["data"]["analysis_id"]

    progress_res = client.get(f"/api/v1/analysis/{analysis_id}/progress")
    assert progress_res.status_code == 200
    body = progress_res.json()
    assert body["success"] is True
    assert body["data"]["analysis_id"] == analysis_id
    assert body["data"]["current_stage"] == "created"

def test_analysis_result_endpoint_requires_parsed_document():
    patient_id = _create_test_patient("Result Patient")
    create_res = client.post("/api/v1/analysis/create", data={"title": "Result Test Session", "patient_id": patient_id})
    analysis_id = create_res.json()["data"]["analysis_id"]
    result_res = client.get(f"/api/v1/analysis/{analysis_id}/result")
    assert result_res.json()["success"] is False
    assert result_res.json()["error"]["code"] == "RESULT_NOT_READY"

def test_quick_start_analysis():
    patient_id = _create_test_patient("QuickStart Patient")
    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "documents", "uploads",
        "33b70989-729d-4bb6-a24a-ccbd31183833_Sample_CBC_Lab_Report.pdf",
    )
    with open(sample_path, "rb") as report_file:
        res = client.post(
            "/api/v1/analysis/quick-start",
            data={"patient_id": patient_id},
            files={"file": ("quick_report.pdf", report_file, "application/pdf")},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["status"] == "uploaded"
    assert "analysis_id" in body["data"]


def test_upload_rejects_invalid_pdf_bytes():
    patient_id = _create_test_patient("Invalid PDF Patient")
    create_res = client.post("/api/v1/analysis/create", data={"title": "Invalid PDF Session", "patient_id": patient_id})
    analysis_id = create_res.json()["data"]["analysis_id"]
    response = client.post(
        f"/api/v1/analysis/{analysis_id}/upload",
        files={"file": ("fake.pdf", b"not a pdf", "application/pdf")},
    )

    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "UPLOAD_HTTP_ERROR"

def test_list_analysis_sessions():
    res = client.get("/api/v1/analysis/sessions")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)

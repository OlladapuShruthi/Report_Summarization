import os
import sys

import pytest

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.finding_event_service import FindingEventService
from app.services.human_confirmation_service import HumanConfirmationService
from app.services.finding_service import FindingService


@pytest.mark.asyncio
async def test_finding_events_are_persisted_and_patient_scoped():
    events = [
        {
            "finding_id": "hemoglobin|g/dl",
            "test_name": "Hemoglobin",
            "date": "2026-01-10",
            "report_id": "jan-cbc",
            "value": 10.2,
            "status": "LOW",
            "evidence_type": "LAB_REPORT",
        }
    ]

    await FindingEventService.replace_for_analysis("patient-a", "analysis-a", events)
    await FindingEventService.replace_for_analysis(
        "patient-b",
        "analysis-b",
        [{**events[0], "report_id": "patient-b-report"}],
    )

    patient_a_events = await FindingEventService.list_for_patient("patient-a")
    patient_b_events = await FindingEventService.list_for_patient("patient-b")

    assert len(patient_a_events) == 1
    assert patient_a_events[0]["analysis_id"] == "analysis-a"
    assert patient_a_events[0]["patient_id"] == "patient-a"
    assert patient_b_events[0]["report_id"] == "patient-b-report"
    assert all(event["patient_id"] == "patient-b" for event in patient_b_events) is True


@pytest.mark.asyncio
async def test_human_confirmation_history_is_separate_from_objective_events():
    confirmation = await HumanConfirmationService.record(
        patient_id="patient-confirmation",
        analysis_id="analysis-confirmation",
        question_id="question-1",
        action="confirm",
        response="The clinician advised follow-up.",
        finding_id="hemoglobin|g/dl",
        evidence_type="PATIENT_REPORTED",
    )

    confirmations = await HumanConfirmationService.list_for_patient("patient-confirmation")

    assert confirmations == [confirmation]
    assert confirmations[0]["evidence_type"] == "PATIENT_REPORTED"
    assert confirmations[0]["finding_id"] == "hemoglobin|g/dl"


@pytest.mark.asyncio
async def test_finding_aggregate_keeps_abnormal_history_after_normal_followup():
    await FindingService.upsert_from_events(
        "patient-lifecycle",
        [
            {
                "finding_id": "hemoglobin|g/dl",
                "test_name": "Hemoglobin",
                "canonical_test_name": "hemoglobin",
                "unit": "g/dL",
                "date": "2026-01-10",
                "report_id": "jan-cbc",
                "value": 10.2,
                "status": "LOW",
                "lifecycle_state": "ACTIVE",
                "evidence_type": "LAB_REPORT",
            },
            {
                "finding_id": "hemoglobin|g/dl",
                "test_name": "Hemoglobin",
                "canonical_test_name": "hemoglobin",
                "unit": "g/dL",
                "date": "2026-04-10",
                "report_id": "apr-cbc",
                "value": 14.0,
                "status": "NORMAL",
                "lifecycle_state": "CURRENTLY_NORMAL",
                "evidence_type": "LAB_REPORT",
            },
        ],
    )

    finding = await FindingService.get_for_patient("patient-lifecycle", "hemoglobin|g/dl")

    assert finding["latest_objective_status"] == "NORMAL"
    assert finding["lifecycle_state"] == "CURRENTLY_NORMAL"
    assert [event["status"] for event in finding["evidence_history"]] == ["LOW", "NORMAL"]

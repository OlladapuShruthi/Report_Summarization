import os
import sys

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.security import create_access_token, decode_access_token
from main import app


client = TestClient(app)


def test_access_token_round_trip_contains_user_subject():
    token = create_access_token("user-123")
    payload = decode_access_token(token)

    assert payload["sub"] == "user-123"
    assert payload["exp"] > 0


def test_access_token_rejects_tampering():
    token = create_access_token("user-123")
    tampered = f"{token[:-1]}x"

    with pytest.raises(HTTPException) as error:
        decode_access_token(tampered)

    assert error.value.status_code == 401


def test_authenticated_patient_access_is_scoped_to_token_owner():
    first = client.post(
        "/api/v1/auth/register",
        json={"full_name": "First Owner", "email": "first-owner@example.com", "password": "password123"},
    ).json()["data"]
    second = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Second Owner", "email": "second-owner@example.com", "password": "password123"},
    ).json()["data"]
    first_token = client.post(
        "/api/v1/auth/login",
        json={"email": "first-owner@example.com", "password": "password123"},
    ).json()["data"]["access_token"]
    second_token = client.post(
        "/api/v1/auth/login",
        json={"email": "second-owner@example.com", "password": "password123"},
    ).json()["data"]["access_token"]

    patient = client.post(
        "/api/v1/patients",
        headers={"Authorization": f"Bearer {first_token}"},
        json={"display_name": "Private Patient"},
    ).json()["data"]

    denied = client.get(
        f"/api/v1/patients/{patient['patient_id']}",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert denied.json()["success"] is False
    assert denied.json()["error"]["code"] in ("ACCESS_DENIED", "PATIENT_NOT_FOUND")
    assert denied.status_code in (403, 404)

    # Part 13: requested user_id mismatching JWT must return 403
    mismatch = client.get(
        "/api/v1/patients",
        headers={"Authorization": f"Bearer {first_token}"},
        params={"user_id": second["user_id"]},
    )
    assert mismatch.status_code == 403
    assert mismatch.json()["success"] is False

    first_patients = client.get(
        "/api/v1/patients",
        headers={"Authorization": f"Bearer {first_token}"},
    ).json()["data"]
    assert [item["patient_id"] for item in first_patients] == [patient["patient_id"]]

    workspace = client.post(
        "/api/v1/analysis/create",
        headers={"Authorization": f"Bearer {first_token}"},
        data={"patient_id": patient["patient_id"]},
    ).json()["data"]
    denied_workspace = client.get(
        f"/api/v1/analysis/{workspace['analysis_id']}",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert denied_workspace.json()["success"] is False
    assert denied_workspace.json()["error"]["code"] in ("ACCESS_DENIED", "WORKSPACE_ACCESS_ERROR")
    assert denied_workspace.status_code in (403, 404)

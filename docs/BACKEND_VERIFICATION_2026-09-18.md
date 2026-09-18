# Backend verification — 2026-09-18

## Scope and evidence

This is a developer verification of the FastAPI backend against the patient-centred project requirements. It used the synthetic fixture `documents/uploads/33b70989-729d-4bb6-a24a-ccbd31183833_Sample_CBC_Lab_Report.pdf` (one digital PDF page, 2,478 bytes). It is not a clinical interpretation of a real patient report.

The API path exercised was:

`register -> login -> create patient -> create analysis -> upload -> parse -> analyze -> result -> timeline`

All calls in this trace returned HTTP 200. The patient created after login had no report or finding data until the report was uploaded.

## Stage trace

| Stage | Actual output | Requirement result |
| --- | --- | --- |
| Authentication | Account registration and login returned a signed bearer token; the analysis session and patient were stored with the same `user_id`. | Pass for the authenticated happy path. |
| Patient creation | `status=created`; `document_info`, `parsed_json`, findings, summary, and execution log were empty. | Pass: creating a patient did not create medical data. |
| Upload | `status=uploaded`; original filename, SHA-256 file hash, size, path, and content type were recorded. | Mostly pass: original source is retained. Duplicate detection requires broader verification. |
| PDF extraction | Digital-PDF extraction; `page_count=1`, `text_density=509.0`, `ocr_used=false`, no warnings; raw and cleaned text were each 509 characters. | Pass for this digital PDF. OCR fallback was not exercised in this run. |
| Classification | `report_type=LAB_REPORT_CBC`; confidence `0.95`; matched seven CBC keywords. | Pass. |
| Deterministic structure | Seven results extracted; no LLM fallback; parser confidence `0.98`; `review_required=false`. | Pass for supported CBC table layout. |
| Objective abnormalities | Hemoglobin `10.2 g/dL` (13.5–17.5), RBC `4.10 million/uL` (4.50–5.90), and hematocrit `34%` (40–50) were correctly flagged outside their report ranges. | Pass. |
| History/comparison | First report: `history_available=false`, `previous_report_count=0`; each abnormal measurement was `NEW_ABNORMAL`, `ACTIVE`, with trend `INSUFFICIENT_HISTORY`. | Pass: it did not invent a previous result or claim resolution. |
| LangGraph | Executed `supervisor -> AnomalyAgent -> RiskAgent -> ConsultAgent -> SummaryAgent -> ValidationAgent`; status `completed`, retry count `0`. | Pass for execution and validation flow. |
| Final validation | `passed=true`, no issues; summary facts matched structured source values. | Pass for factual grounding of this trace. |
| Timeline persistence | Seven objective finding events appeared with the active `patient_id`, `analysis_id`, report ID, values, and evidence type `LAB_REPORT`. | Pass in in-memory/local execution only. The health endpoint reports MongoDB as `not_configured_or_down`, so durable MongoDB persistence was not proved. |

## Extracted structured output

| Test | Value | Reference range | Outside range |
| --- | ---: | --- | --- |
| Hemoglobin | 10.2 g/dL | 13.5–17.5 | Yes |
| RBC | 4.10 million/uL | 4.50–5.90 | Yes |
| WBC | 8,400 cells/uL | 4,000–11,000 | No |
| Platelets | 250,000 /uL | 150,000–450,000 | No |
| Hematocrit | 34% | 40–50 | Yes |
| MCV | 82 fL | 80–100 | No |
| MCH | 27 pg | 27–33 | No |

## Actual analysis output (important safety issue)

The pipeline classified the three out-of-range values as `Marked`, summed them to score 9, and emitted:

```json
{
  "risk_level": "CRITICAL",
  "consultation_required": true,
  "recommended_specialist": "Physician",
  "urgency": "Immediate"
}
```

This is internally consistent with the current code, but it is not adequately clinically calibrated: the risk agent converts the *count* of three `Marked` findings into `CRITICAL`/`Immediate` without clinical thresholds, symptoms, patient context, or an explicit medical rule set. It does not meet the target requirement for evidence-based, non-diagnostic risk guidance. Treat this as a release blocker until reviewed clinical rules replace the count-based scoring.

## Automated test result

Command run:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Result: **49 passed, 14 failed, 1 skipped, 2 errors**.

The two errors were filesystem permission failures while pytest attempted to create locks under the shared Windows temporary directory. The failures are functional/API regressions, not just test noise:

1. `POST /api/v1/patients` rejects the documented `display_name` input with HTTP 422. The Pydantic model currently requires its legacy alias `name`; this violates the required API contract and breaks the backend tests.
2. The token-tampering regression test fails. Changing the final base64url character can preserve the decoded bytes because non-significant padding bits are not canonicalized before signature verification. Token parsing must reject non-canonical encodings as well as invalid signatures.
3. The API tests that still call patient/analysis endpoints without credentials consequently fail (or conflict with the new ownership behaviour). The test suite and intended production authentication contract need to be made consistent.

## Requirement-gap verdict

The CBC parsing and deterministic analysis happy path works. The backend is **not ready to claim full compliance** with the supplied end-to-end requirements because of these priority gaps:

1. **P0 — security:** routes use `get_optional_user_id`; unauthenticated callers can still create and operate on unowned patient records. The specification requires bearer authentication and ownership enforcement for every patient-scoped operation.
2. **P0 — API correctness:** `display_name` is rejected despite being the specified request field.
3. **P0 — safety:** count-based risk scoring escalates this synthetic CBC to `CRITICAL` and `Immediate`; replace it with clinically reviewed, explainable thresholds and conservative language.
4. **P1 — longitudinal dates:** the sample contains `Date: 26-Jul-2026`, but parsed patient metadata lacks `report_date`; comparison falls back to the upload/session timestamp, contrary to the clinical-date requirement.
5. **P1 — canonical persistence:** the running health check reports the MongoDB database `not_configured_or_down`; the backend is falling back to process-local memory. This cannot meet the longitudinal-history requirement across a process restart or deployment.
6. **P1 — production readiness:** the current status documents list unimplemented/partial PHI-safe audit logs, strict authentication mode, chat-answer validation, provenance expansion, malware scanning, rate limiting, and operational health checks.

No application source code was changed as part of this verification.

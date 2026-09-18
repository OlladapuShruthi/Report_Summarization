# Development Status and Handoff

**Project:** Patient-Centric Longitudinal Medical Report Assistant  
**Last updated:** 2026-09-08  
**Status owner:** Development handoff document

## How to Use This File

Update this file at the end of every development session and after each meaningful feature or verification step. Keep the latest checkpoint near the top. Do not mark work complete only because code exists; mark it complete after a focused test or manual verification succeeds.

Status meanings:

- `[x]` Verified working for the documented scope
- `[~]` Partially implemented, fallback, prototype, or limited in scope
- `[ ]` Not implemented
- `[!]` Blocking correctness, security, or release readiness

## Current Checkpoint

- **Development phase:** Post-Sprint 4B; backend hardening and longitudinal intelligence
- **Current priority:** Comparison correctness -> human-in-the-loop uncertainty handling -> comparison-aware LangGraph context
- **Last verified baseline:** Core parsing, report analysis, patient-scoped history/comparison, RAG/chat prototype, and automated tests are present.
- **Latest completed slice:** Comparison history now preserves source report IDs and evidence types for historical and current measurements.
- **Latest completed slice:** Parser review reasons now create persisted review questions with API responses labeled as patient-reported or unknown.
- **Latest completed slice:** Comparison context now exposes normalized, report-linked `finding_events` for every observed measurement.
- **Latest completed slice:** Finding events now have a separate MongoDB/in-memory persistence service and are returned in the patient timeline.
- **Latest completed slice:** Comparisons and finding events now expose normalized lifecycle states without changing existing factual finding statuses.
- **Latest completed slice:** Human responses are stored separately from objective finding events and may reference a finding without changing its laboratory evidence.
- **Latest completed slice:** Patient timelines now expose objective `finding_events` and patient-reported `human_confirmations` as separate evidence streams.
- **Latest completed slice:** LangGraph now receives patient confirmations as separate context and summaries explicitly label them as non-objective evidence.
- **Latest completed slice:** Review policy now distinguishes pending questions from acknowledged questions and never unblocks analysis without objective evidence.
- **Latest completed slice:** Follow-up reports now create new linked patient-scoped analysis sessions instead of replacing unresolved original evidence.
- **Latest completed slice:** Signed access tokens and authenticated ownership checks now cover patients, analysis workspaces, and chat/RAG access.
- **Latest completed slice:** Persistent patient-scoped finding aggregates now retain objective evidence history and latest lifecycle state.
- **Latest completed slice:** The complete backend suite passes in the configured project `.venv` with MedSpaCy and FAISS installed.
- **Safe continuation point:** Start with the existing comparison service and tests. Do not redesign the parser or add unrelated frontend screens before the backend contracts for uncertainty and confirmation are defined.
- **Working tree note:** The repository may contain uncommitted implementation changes. Preserve existing user changes when continuing.

## Current System Flow

1. Select a patient workspace.
2. Upload a PDF or image report.
3. Extract text with direct PDF extraction or OCR fallback.
4. Clean and classify the report.
5. Extract structured lab or narrative data.
6. Validate the Medical JSON contract.
7. Persist the analysis workspace and parsed data.
8. Retrieve patient-scoped history.
9. Compare compatible current and previous measurements.
10. Run the LangGraph anomaly, risk, consultation, summary, and validation workflow.
11. Store and display the result.
12. Answer patient-scoped chat questions through intent classification, retrieval, and grounded generation/fallback.

## Verified Complete for Supported Scope

- [x] FastAPI upload, analysis workspaces, API response wrappers, and progress endpoints.
- [x] Digital PDF extraction with strict `%PDF-` signature validation.
- [x] Real Tesseract + Poppler OCR fallback validated with a scanned CBC round trip.
- [x] Text cleaning and report classification for supported report categories.
- [x] Deterministic table-aware and label/value lab extraction for the supported analytes.
- [x] Narrative/cardio sample protection against false CBC extraction.
- [x] Medical JSON construction with Pydantic and semantic validation.
- [x] Parser abstention and `review_required` / `needs_review` handling for unsafe or uncertain extraction.
- [x] LangGraph conditional routing through anomaly, risk, consultation, summary, and validation agents.
- [x] Validation checks for source-fact mismatch, omitted abnormal findings, contradictions, and invented resolution for unknown comparisons.
- [x] Summary validation retry path, limited to summary regeneration.
- [x] Patient profile creation, patient selection, and patient-scoped analysis workspaces.
- [x] Patient history retrieval and deterministic same-name/same-unit comparison foundation.
- [x] `UNKNOWN` and `CURRENTLY_NORMAL` comparison safeguards for missing or normalized evidence.
- [x] Timeline and result APIs/UI for the current patient workspace.
- [x] Intent classifier, patient-scoped chat API, chat history API, and React chat view.
- [x] FAISS index persistence and metadata filtering for patient report chunks.
- [x] Deterministic chat fallback when Groq is unavailable or fails.
- [x] Automated parser, comparison, graph, validation, backend, and RAG/chat test coverage for the current scope.

## Partial or Prototype Quality

- [~] MedSpaCy is optional and currently provides narrative sentence/section processing; clinical entity and section configuration remain.
- [~] LLM structured extraction is a bounded fallback and must remain behind schema/semantic validation. Live model output has previously been unreliable for strict JSON.
- [~] Groq summary/chat integration depends on credentials, model behavior, rate limits, and fallback handling.
- [~] Comparison supports a limited reviewed engineering catalogue; aliases, units, dates, provenance, and complete timeline handling need expansion.
- [~] FAISS uses a development embedding strategy; a verified production embedding model is still required.
- [~] MongoDB has an in-memory fallback, which is useful for local tests but is not production persistence.
- [~] Frontend supports the main upload, analysis, results, timeline, and chat flow but does not yet expose the complete review/confirmation workflow.

## Not Yet Implemented or Release Blocking

- [ ] Persistent finding lifecycle and finding-event models.
- [ ] Human-in-the-loop APIs for pending questions, follow-up uploads, patient confirmation, no-report-available, dismiss, and defer actions.
- [ ] Persisted human answers with timestamp, user, evidence type, and related finding ID.
- [ ] Comparison-aware LangGraph history preparation and explicit review routing.
- [ ] Complete authenticated account flow and JWT/token handling.
- [ ] Enforce `user_id + patient_id` ownership on every patient, report, analysis, timeline, result, and chat operation.
- [ ] Production embedding model and retrieval-quality evaluation.
- [ ] Chat answer validation for unsupported historical claims and medical advice.
- [ ] Report metadata separation, duplicate detection, immutable source provenance, and report date versus upload timestamp.
- [ ] OCR confidence, page-level warnings, image preprocessing, and mixed digital/scanned PDF tests.
- [ ] Complete frontend review-required, uncertainty, confirmation, and protected-route states.
- [ ] PHI-safe logging, audit logging, secrets management, rate limits, malware scanning, and operational health checks.

## Backend Completion Checkpoint

- **Validated command:** `.venv\Scripts\python.exe -m pytest -q`
- **Result:** 64 passed, 1 skipped.
- **Environment:** project `.venv`, Python 3.13.2, MedSpaCy and FAISS available.
- **Skipped test:** one environment-dependent integration test; no test failures remain in the configured environment.
- **Warnings:** existing `datetime.utcnow()` deprecations, Starlette/httpx deprecation warning, and MedSpaCy matcher warning remain for cleanup.
- **Backend handoff:** backend feature development can now pause for frontend integration. Production hardening items remain documented below.
## Active Development Plan

### Step 1: Complete longitudinal comparison

- Inspect and extend the existing comparison service rather than replacing it.
- Match canonical test identity and compatible units conservatively.
- Retrieve the complete available patient timeline.
- Preserve current/previous values, units, dates, reference ranges, source report IDs, trend, status, and uncertainty reason.
- Add tests for low -> normal, low -> low improving, low -> low worsening, low -> normal -> low recurrence, missing current measurement, and no previous report.

**Completion evidence required:** focused comparison tests pass and output contains sufficient evidence to explain every status.

### Step 2: Add persisted human-in-the-loop handling

- Create a structured review-question/confirmation contract.
- Generate questions only for material uncertainty, missing follow-up evidence, identity ambiguity, or unsafe extraction.
- Support upload follow-up, confirm patient-reported status, no report available, dismiss, and defer.
- Store the question, answer, timestamp, authenticated user, evidence type, and related finding ID.
- Keep patient-reported resolution separate from objective laboratory normalization.

**Completion evidence required:** API tests prove questions and answers persist and unresolved questions do not become normal findings.

### Step 3: Feed reliable history into LangGraph

- Extend graph state with `patient_id`, historical context, review state, finding events, and evidence warnings.
- Add deterministic history/context preparation before risk reasoning.
- Keep comparison logic outside the LLM agents.
- Route unsafe or unresolved material uncertainty to human review.
- Require summary output to state available-history limitations and objective versus patient-reported evidence.

**Completion evidence required:** graph tests cover review routing, unknown status, objective normalization, recurrence, and patient-reported resolution.

### Step 4: Harden RAG and chat

- Keep MongoDB as the source of truth for structured patient facts and comparisons.
- Upgrade and verify embeddings.
- Index report chunks, narrative sections, and provenance metadata.
- Validate answers against retrieved facts and reject unsupported historical claims.
- Add cross-patient isolation and restart-persistence integration tests.

### Step 5: Add account ownership and security

- Implement login/signup/session handling.
- Add authenticated `user_id` ownership to every patient-scoped read and write.
- Add PHI-safe logs, audit events, input limits, secret validation, and operational checks.

### Step 6: Finalize frontend against stable contracts

- Add protected routes and session expiry.
- Add review-required and human-confirmation views.
- Add detailed evidence, uncertainty, comparison, and finding-history views.
- Ensure loading, empty, error, retry, and patient-scope states are handled consistently.

## Important Architecture Rules

- MongoDB is the source of truth for patients, reports, parsed facts, findings, comparisons, confirmations, and chat records.
- FAISS is a retrieval index, not the authoritative patient database.
- LangGraph state/checkpointing is workflow execution memory, not the complete patient history.
- Patient data must never be retrieved across `patient_id` boundaries.
- Final account-level isolation must enforce both `user_id` and `patient_id`.
- Deterministic parsing owns objective extraction; LLMs may assist only through strict validated contracts.
- The Validation Agent checks consistency and unsupported claims; it does not clinically certify a diagnosis.
- Missing evidence must remain `UNKNOWN`, `NOT_MEASURED`, or review-required. It must never silently become normal.
- The system is assistive and non-diagnostic.

## Validation Commands

Run from the repository root with the project virtual environment active:

```powershell
pytest -q
```

For a focused backend slice:

```powershell
pytest -q tests/test_parser.py tests/test_comparison.py tests/test_graph.py tests/test_validation_agent.py tests/test_chat_rag.py tests/test_faiss_rag_chat.py
```

For the frontend production build:

```powershell
Set-Location frontend
npm run build
```

Before reporting completion, record the command run, result, and any environment limitations in the session log below.

## Session Log

### 2026-09-08

- Created this handoff document as the single development-status reference.
- Confirmed the project baseline is the functional parsing, analysis, patient-history, comparison, RAG, and chat prototype.
- Completed the first comparison-hardening slice: preserved historical/current report IDs and `LAB_REPORT` evidence types in comparison history.
- Updated analysis and RAG retrieval call sites to pass the active analysis ID into comparison context.
- Added a regression test for report-ID evidence preservation.
- Validation: `pytest -q tests/test_comparison.py` -> 7 passed.
- Added the first human-in-the-loop slice: persisted review questions, pending-question retrieval, and `confirm` / `no_report` / `dismiss` / `defer` response actions.
- Added API coverage proving a patient confirmation is stored as `PATIENT_REPORTED`.
- Validation: `pytest -q tests/test_backend.py -k "uncertain_real_report_requires_review"` -> 1 passed.
- Added normalized `finding_events` to comparison context with finding identity, date, report ID, value, status, and evidence type.
- Added regression coverage for event ordering and current-event marking.
- Validation: `pytest -q tests/test_comparison.py` -> 7 passed.
- Added `FindingEventService` with replace-per-analysis persistence and patient-scoped retrieval.
- Added finding-event data to the patient timeline response.
- Added cross-patient isolation coverage for persisted events.
- Validation: `pytest -q tests/test_finding_events.py` -> 1 passed.
- Added lifecycle mapping: `ACTIVE`, `IMPROVING`, `WORSENED`, `PERSISTENT`, `CURRENTLY_NORMAL`, and `UNKNOWN`.
- Confirmed missing measurements remain `UNKNOWN` and normal follow-up remains `CURRENTLY_NORMAL`, not clinical resolution.
- Validation: `pytest -q tests/test_comparison.py` -> 7 passed.
- Added `HumanConfirmationService` with MongoDB/in-memory persistence for patient responses.
- Added optional `finding_id` linkage to review responses; objective finding events are never overwritten.
- Confirmations use `PATIENT_REPORTED` only for explicit confirmation and `UNKNOWN` for other review actions.
- Validation: `pytest -q tests/test_backend.py -k "uncertain_real_report_requires_review"` -> 1 passed.
- Added patient-scoped confirmation history retrieval to the timeline response without merging it into objective events.
- Added regression coverage proving confirmation evidence remains separate and patient-scoped.
- Validation: `pytest -q tests/test_finding_events.py` -> 2 passed.
- Extended `GraphState` and runtime with `patient_id` and `human_confirmations`.
- Passed patient confirmations into analysis execution without allowing them to change anomaly or lifecycle calculations.
- Added summary wording that distinguishes patient-reported context from objective report measurements.
- Validation: `pytest -q tests/test_graph.py tests/test_validation_agent.py` -> 7 passed; integrated suite -> 28 passed.
- Added explicit review policy states: `not_required`, `pending`, and `acknowledged`.
- Confirmed `analysis_allowed` remains false for acknowledged review when objective evidence is still insufficient.
- Updated API progress, result, and review-question responses with the policy decision.
- Validation: `pytest -q tests/test_backend.py -k "uncertain_real_report_requires_review"` -> 1 passed.
- Added `POST /api/v1/analysis/{analysis_id}/follow-up` to create a new linked session for follow-up evidence.
- Original sessions remain unchanged; the new session stores `follow_up_for_analysis_id` and stays patient-scoped.
- Validation: `pytest -q tests/test_backend.py -k "follow_up_upload"` -> 1 passed.
- Added signed HMAC access tokens to login responses with expiry and tamper rejection.
- Added token-owner checks for patient records, analysis workspaces, follow-up uploads, review endpoints, and chat/history operations.
- Added cross-account isolation tests for patients and analysis workspaces.
- Validation: `pytest -q tests/test_auth_security.py` -> 3 passed; chat/RAG/auth suite -> 12 passed.
- Security caveat: unauthenticated legacy development mode remains compatible with existing tests; production deployment must require bearer authentication on all patient-scoped routes.
- Added `FindingService` persistence for finding identity, first/last observation, latest objective status, lifecycle state, and evidence history.
- Added finding aggregates to patient timeline responses without replacing raw finding events.
- Verified low -> normal retains the original low evidence and reports `CURRENTLY_NORMAL` as the latest lifecycle state.
- Validation: full backend regression suite -> 42 passed.
- Exact next step: add explicit production `AUTH_REQUIRED`, migrate frontend requests later, and harden comparison/provenance and RAG answer validation.

### Next Session Template

Copy this section for each new session:

```text
### YYYY-MM-DD

- Goal:
- Files changed:
- Behavior added or fixed:
- Tests/commands run:
- Result:
- Known limitations:
- Exact next step:
```

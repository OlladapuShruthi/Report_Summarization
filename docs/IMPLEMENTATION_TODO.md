# Implementation TODO

This is the working implementation backlog for the patient-centric, longitudinal, human-in-the-loop medical report assistant.

The checklist reflects the verified repository state as of 2026-09-06. It does not mark a feature complete merely because a class, endpoint, or fallback exists.

## Status Legend

- [x] Verified working for the supported scope
- [~] Partially implemented or prototype quality
- [ ] Not implemented
- [!] Blocking correctness or production readiness

## Current Baseline

- [x] FastAPI application, upload flow, analysis workspaces, and API response wrappers.
- [x] MongoDB connector with in-memory fallback.
- [x] Digital PDF extraction through pdfplumber with strict PDF signature validation.
- [~] Deterministic and table-aware laboratory extraction; broader analyte coverage remains.
- [x] Narrative/cardio sample is routed to narrative review and cannot produce a false CBC analysis.
- [x] Native Tesseract and Poppler installed and validated through a real CBC OCR round trip.
- [~] MedSpaCy/spaCy narrative processing tier is integrated; clinical section/entity configuration remains.
- [~] Strict LLM structured-extraction fallback; live Groq connectivity works, but the selected model returned non-JSON and must be treated as unreliable until structured output is enforced.
- [x] LangGraph nodes and conditional routing for the current report-level workflow.
- [~] Groq summary/chat integration; credentials are configured locally, but live model output/rate limits still require robust handling.
- [~] Patient history/comparison services implement UNKNOWN and CURRENTLY_NORMAL safeguards; persistent finding/event models remain.
- [x] FAISS patient isolation and on-disk index/metadata persistence are implemented; production embedding model remains.
- [x] Automated suite and real CBC/cardio/OCR coverage pass; broader scanned-report corpus remains.

## Phase 0 - Correctness and Safety Blockers

- [x] Prevent false successful analysis when extraction is empty, corrupted, ambiguous, or implausibly sparse.
  - Add extraction quality gates.
  - Reject invalid PDF byte content instead of decoding it as plain text.
  - Require minimum classification confidence and structured evidence.
  - Persist parser warnings and make the API status `needs_review` when appropriate.
- [~] Fix narrative report classification.
  - Add section/layout-aware signals.
  - Add tie handling when multiple report types have similar scores.
  - Never route prose to the laboratory parser solely because it contains a test word.
- [x] Prevent laboratory false positives for tested narrative/cardio samples.
  - Require structured row/column or label-value evidence.
  - Do not extract a test from arbitrary narrative prose.
  - Preserve source span/page/line provenance for every measurement.
- [x] Add parser abstention and review-required analysis blocking.
  - The parser must be able to return `UNKNOWN` or `REVIEW_REQUIRED`.
  - Downstream clinical reasoning must not run on untrusted extraction.
- [~] Remove the database credential from source code; external credential rotation remains an operational task.

## Phase 1 - Production Document Processing

### PDF and OCR

- [x] Install and verify native Tesseract OCR on this Windows environment.
- [x] Install and verify Poppler binaries required by pdf2image.
- [~] Add OCR engine/version/configuration to parser metadata.
- [ ] Add image preprocessing: deskew, grayscale, contrast, scale, and orientation handling.
- [ ] Add OCR confidence and page-level warnings.
- [~] Add real scanned-image OCR coverage generated from the CBC PDF.
- [ ] Add tests for OCR failure, missing executable, unreadable page, and mixed digital/scanned PDFs.

### Parser Tiering

- [~] Add optional spaCy and MedSpaCy dependencies with a documented model setup.
- [~] Implement the secondary MedSpaCy narrative processing tier; clinical entity/section configuration remains.
- [x] Define when deterministic extraction is accepted and when MedSpaCy is invoked.
- [x] Implement the LLM structured-extraction fallback using strict JSON schema output.
- [~] Record `llm_used` and model/fallback metadata; prompt version and latency remain.
- [x] Ensure LLM extraction cannot bypass Pydantic and semantic validation.
- [x] Reject invalid or unsupported LLM output; bounded retry remains.

### Medical JSON Contract

- [ ] Align the implementation contract with the documented names: `lab_results` versus `lab_facts`, `narrative_impressions` versus `narrative_findings`.
- [ ] Add report ID, source document ID, report date, upload timestamp, and source provenance.
- [ ] Preserve the reference range exactly as supplied by each report.
- [ ] Add semantic validation for units, dates, duplicate measurements, impossible values, and source provenance.
- [ ] Separate parser confidence from clinical interpretation confidence.
- [ ] Add contract version migration tests.

## Phase 2 - Patient Health Record Foundation

- [x] Patient profile creation and patient-scoped workspaces.
- [~] Patient-scoped history retrieval.
- [ ] Define persistent models/collections for:
  - `patients`
  - `reports`
  - `measurements`
  - `findings`
  - `finding_events`
  - `comparisons`
  - `human_confirmations`
  - `chat_messages`
- [ ] Store report metadata separately from parsed measurements.
- [ ] Store both `report_date` and `uploaded_at`.
- [ ] Use report date as the primary clinical timeline date.
- [ ] Add source/evidence types: `LAB_REPORT`, `IMAGING_REPORT`, `CLINICAL_NOTE`, `PATIENT_REPORTED`, `CLINICIAN_REPORTED`, `UNKNOWN`.
- [ ] Add immutable evidence references to source report, page, line/span, and user confirmation.
- [ ] Add report duplicate detection using file hash, patient, report date, report type, and content similarity.
- [ ] Link duplicate uploads instead of creating repeated clinical events.
- [ ] Add timeline coverage metadata so the system states that history is only the available uploaded history.
- [ ] Add authenticated user ownership and enforce `user_id + patient_id` scoping on every read/write.

## Phase 3 - Longitudinal Finding Lifecycle

- [ ] Define finding lifecycle states:
  - `ACTIVE`
  - `PERSISTENT`
  - `IMPROVING`
  - `WORSENED`
  - `CURRENTLY_NORMAL`
  - `PATIENT_REPORTED_RESOLVED`
  - `UNKNOWN`
- [ ] Keep historical findings permanently; never delete an abnormal finding because a later value is normal.
- [ ] Distinguish objective laboratory normalization from clinical resolution.
- [ ] Create finding identity using canonical test identity, analyte/code where available, patient, and compatible units.
- [ ] Track first observed, last observed, latest objective status, and evidence history.
- [ ] Represent a missing measurement as `NOT_MEASURED` or `UNKNOWN`, never `NORMAL`.
- [ ] Distinguish `FIRST_OBSERVED_IN_SYSTEM` from first occurrence in the patient's life.
- [ ] Store patient/clinician confirmations as separate events, never as replacement objective evidence.
- [ ] Add tests for:
  - low -> normal
  - low -> low with improvement
  - low -> low with worsening
  - old finding absent from current report
  - different report types
  - no previous report
  - gaps in available history
  - patient-reported resolution without follow-up report

## Phase 4 - Comparison Engine

- [x] Existing same-name/same-unit comparison provides a deterministic starting point.
- [x] Comparison produces evidence-aware UNKNOWN and CURRENTLY_NORMAL states.
- [ ] Retrieve the complete available patient timeline, not only the latest session.
- [ ] Match canonical tests and aliases conservatively.
- [~] Preserve each measurement's value, unit, date, reference range, and source report; report IDs/provenance need expansion.
- [ ] Normalize units only through reviewed conversion rules.
- [ ] Refuse comparison when units or analyte identity are uncertain.
- [ ] Evaluate each value against its own report-provided reference range.
- [x] Produce structured comparison output with:
  - current measurement
  - previous comparable measurement
  - trend
  - longitudinal status
  - evidence type
  - evidence report IDs
  - uncertainty reason
- [x] Add missing-measurement comparison warnings through UNKNOWN status.
- [ ] Add clinician-reviewed rules for aliases, unit conversions, and special analytes.

## Phase 5 - Human-in-the-Loop

- [~] Add a structured `review_required` state to the analysis/session contract; parser-to-analysis blocking is implemented, but user acceptance APIs remain.
- [x] Trigger analysis blocking for material extraction/classification uncertainty.
- [ ] Trigger questions only for material uncertainty, missing follow-up evidence, identity ambiguity, or unsafe extraction.
- [ ] Support these actions:
  - upload a follow-up report
  - confirm patient-reported status
  - state that no report is available
  - dismiss or defer the question
- [ ] Store question, answer, timestamp, user, evidence type, and related finding ID.
- [ ] Represent confirmation as `PATIENT_REPORTED_RESOLVED`, not objective resolution.
- [ ] Ensure unresolved questions do not silently become normal findings.
- [ ] Add APIs for pending questions, answering questions, and attaching follow-up reports.
- [ ] Add frontend review states before final result display where necessary.

## Phase 6 - LangGraph Integration

- [~] Current graph supports anomaly, risk, consultation, summary, validation, and retry.
- [ ] Extend `GraphState` with:
  - `patient_id`
  - `historical_context`
  - `comparison_context`
  - `review_required`
  - `finding_events`
  - `evidence_warnings`
- [ ] Add a deterministic history/context preparation node before risk reasoning.
- [ ] Keep comparison logic outside the LLM agents.
- [ ] Route to human review when required evidence is missing or unsafe.
- [ ] Prevent risk analysis from treating unknown findings as normal.
- [ ] Update Risk Agent to use current abnormalities plus reliable longitudinal context.
- [ ] Update Consult Agent to distinguish current abnormality, persistent trend, and uncertainty.
- [ ] Update Summary Agent to explicitly state:
  - current result
  - historical comparison
  - available-history limitation
  - missing measurement uncertainty
  - objective versus patient-reported evidence
- [ ] Strengthen Validation Agent to detect unsupported claims, contradictions, invented resolution, and omitted uncertainty.
- [ ] Add graph tests for review routing, unknown status, objective normalization, and patient-reported resolution.

## Phase 7 - RAG and Chat

- [x] Intent classifier, patient-scoped retrieval, chat API, and deterministic fallback.
- [~] FAISS vector search with patient isolation.
- [x] Persist FAISS index and metadata across process restarts.
- [ ] Install and verify a production embedding model; do not silently treat hash vectors as semantic embeddings in production.
- [ ] Keep MongoDB as the source of truth for structured comparisons.
- [ ] Index source report chunks, narrative sections, clinical knowledge, and provenance metadata.
- [ ] Do not use vector similarity to determine whether a measurement existed.
- [ ] Supply chat LLM prompts with backend-generated structured history and comparison context.
- [ ] Add response validation for unsupported historical claims and medical advice.
- [ ] Add clarification behavior for insufficient history, missing tests, and uncertain comparisons.
- [ ] Add cross-patient isolation and restart-persistence integration tests.

## Phase 8 - Authentication, Privacy, and Operations

- [ ] Implement authentication APIs and password/token handling.
- [ ] Add user ownership checks to every patient, report, timeline, result, and chat endpoint.
- [ ] Encrypt sensitive data in transit and at rest where applicable.
- [ ] Add audit logging for report access, analysis, confirmations, exports, and deletion.
- [ ] Add configurable retention and deletion workflows.
- [ ] Add PHI-safe application logging and error responses.
- [ ] Add rate limits, upload limits, MIME/content validation, and malware scanning.
- [ ] Add secrets management and environment validation at startup.
- [ ] Add operational health checks for MongoDB, OCR, LLM, FAISS/vector storage, and external integrations.

## Phase 8A - Frontend and API Completion

- [~] Patient selection and patient-scoped workspace flow.
- [~] Upload, parsing progress, analysis progress, results, timeline, and chat views.
- [ ] Add the complete authentication flow: home, login, signup, logout, session expiry, and protected routes.
- [ ] Add patient management: create, select, update, archive, and view patient details.
- [ ] Add report management: list, view metadata, download original file, download processed report, and delete according to retention policy.
- [ ] Add analysis controls with explicit states for parsing, review required, analyzing, completed, and failed.
- [ ] Add human-review UI for missing evidence, uncertain extraction, follow-up upload, and patient confirmation.
- [ ] Add detailed results views for current measurements, evidence, finding history, uncertainty, comparisons, risk, consultation, and validation.
- [ ] Add timeline filters by date, report type, finding, and evidence type.
- [ ] Add settings for language, notifications, retention, and account preferences where supported by backend APIs.
- [ ] Add export/share flows only after access control and PHI-safe redaction are implemented.
- [ ] Ensure every frontend request handles authentication, patient scope, loading, empty, review-required, error, and retry states.

## Phase 8B - External Sources and Integration Boundaries

- [ ] Define the external-source boundary for clinical guidelines and lab reference ranges.
- [ ] Store source name, version, retrieval date, license/usage constraints, and provenance for imported knowledge.
- [ ] Keep external clinical knowledge separate from patient facts and never use it as proof that a patient has a condition.
- [ ] Define optional integration contracts for hospital EHR/FHIR, laboratory systems, health APIs, and voice-to-text.
- [ ] Require explicit patient/account authorization before importing or exporting external health data.
- [ ] Add integration failure, timeout, retry, and revocation handling.

## Phase 8C - Deployment, Reproducibility, and Clinical Governance

- [ ] Pin Python, Node, OCR, Poppler, spaCy, MedSpaCy, model, and vector-library versions.
- [ ] Provide reproducible local and deployment setup for native OCR binaries and NLP models.
- [ ] Add startup validation that reports unavailable capabilities without silently enabling unsafe fallbacks.
- [ ] Add separate development, test, and production configuration validation.
- [ ] Add structured metrics for extraction quality, review-required rate, LLM fallback rate, latency, and failures.
- [ ] Add tracing/correlation IDs across upload, parse, graph, comparison, chat, and persistence operations.
- [ ] Define clinician review of comparison rules, units, reference ranges, risk thresholds, and consultation wording.
- [ ] Document that the system is assistive and non-diagnostic, including escalation guidance and limitations.
- [ ] Define a clinical evaluation set with expected extraction, comparison, uncertainty, and safety outcomes.
- [ ] Define a change-control process for prompts, models, parser rules, clinical rules, and schema versions.

## Phase 9 - Test and Release Gate

- [x] Existing unit suite passes in the Python 3.10 environment.
- [x] Add real PDF fixture tests for clean CBC, narrative/cardio, malformed PDF, and unsupported document.
- [x] Add OCR integration tests in a configured environment.
- [~] Add MedSpaCy extraction tests; dependency/model versions still need pinning.
- [~] Add live Groq tests behind an explicit opt-in environment flag; live HTTP works but model JSON output was invalid and a retry was rate-limited.
- [x] Add LLM invalid JSON, schema-invalid, and fallback tests.
- [x] Add end-to-end API tests from upload through result and human review blocking.
- [x] Add persistence tests across vector-store reload.
- [ ] Add patient isolation tests for MongoDB, vector search, timeline, and chat.
- [x] Add regression test preventing the cardio sample from becoming a low-risk false success.
- [ ] Add frontend build and workflow tests for patient selection, upload, progress, results, timeline, review, and chat.
- [ ] Update project documentation only after behavior is verified by tests.

## Recommended Execution Order

1. Phase 0 correctness blockers.
2. Phase 1 document processing and parser abstention.
3. Phase 2 patient record data contracts.
4. Phase 3 finding lifecycle.
5. Phase 4 comparison engine.
6. Phase 5 human-in-the-loop APIs and review states.
7. Phase 6 LangGraph integration.
8. Phase 7 persistent RAG/chat.
9. Phase 8 security and operations.
10. Phase 8A frontend and API completion.
11. Phase 8B external-source and integration boundaries.
12. Phase 8C deployment and clinical governance.
13. Phase 9 release validation.

## Definition of Done for the Next Slice

The next coding slice should not be considered complete until the system can:

1. Parse a clean CBC sample correctly.
2. Reject or request review for the cardio/narrative sample instead of returning a false low-risk result.
3. Represent a missing historical measurement as `UNKNOWN`.
4. Compare two measurements using their own dates, units, and reference ranges.
5. Preserve the previous finding and its evidence when a later measurement is normal.
6. Run tests proving those behaviors.

## Next Steps Queue

### P0 - Finish Safety Contracts

- [ ] Add first-class measurement, finding, finding-event, comparison, and human-confirmation persistence models.
- [ ] Add report date, upload date, source document ID, page/line provenance, and evidence type to every measurement.
- [ ] Add APIs to accept/reject review-required reports and attach follow-up evidence.
- [ ] Add review UI for uncertain extraction and missing historical measurements.
- [ ] Add prompt version, latency, model, and fallback reason to LLM metadata.
- [ ] Add Groq retry/backoff, rate-limit handling, and structured-output enforcement where the provider/model supports it.

### P1 - Improve Clinical Extraction Quality

- [ ] Configure MedSpaCy clinical section/entity rules and pin compatible spaCy/MedSpaCy versions.
- [ ] Expand the clinician-reviewed analyte/catalogue and table parser coverage.
- [ ] Add OCR confidence, page-level provenance, preprocessing, and mixed digital/scanned PDF tests.
- [ ] Add strict ambiguity thresholds for table rows, units, reference ranges, and report classification.
- [ ] Add report duplicate detection and timeline coverage metadata.

### P1 - Complete RAG and Data Persistence

- [ ] Install and validate a production embedding model instead of the hash fallback.
- [ ] Add vector index versioning, atomic writes, corruption recovery, and rebuild tooling.
- [ ] Add source provenance to indexed chunks and response citations.
- [ ] Validate chat answers for unsupported historical claims and unknown measurements.

### P2 - Security and Product Completion

- [ ] Rotate the previously exposed MongoDB credential outside the repository.
- [ ] Add authentication and user ownership checks to all patient/report/chat operations.
- [ ] Add PHI-safe logging, audit events, retention/deletion, and upload malware/content validation.
- [ ] Add frontend review, finding-history, evidence, and uncertainty views.
- [ ] Add clinician review and version control for risk thresholds, comparison rules, and prompts.

### Current Release Gate

- [x] Python 3.10 backend suite: `57 passed`.
- [x] Clean CBC, cardio narrative, malformed PDF, and OCR sample validation.
- [x] Native Tesseract and Poppler installed locally.
- [x] Persistent FAISS reload and patient isolation tests.
- [ ] Live Groq structured-output test passes without rate-limit or invalid-format failure.
- [ ] MongoDB credential rotated externally.
- [ ] Human review acceptance workflow implemented end to end.

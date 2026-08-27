# AI Medical Report Assistant - Living Technical Documentation

This document serves as the **single source of truth** for the architecture, data structures, module designs, API catalog, and development roadmap of the AI Medical Report Assistant. It is continuously updated at every phase of development.

---

## 🏛️ System Architecture & Layered Workflow

Below is the complete layered technical workflow for the AI Medical Report Assistant:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               1. Web UI (React + Vite)                                 │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 2. API Layer (FastAPI)                                 │
│  Standard Envelope: { "success": true, "message": "...", "data": {...}, "error": null }│
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                3. Service Layer                                        │
│                        (ParsingService, AnalysisService)                               │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                4. Operating Modes                                      │
│                                                                                        │
│  ┌─────────────────────────────┐ ┌───────────────────────────┐ ┌─────────────────────┐ │
│  │   Analysis Mode             │ │   Conversation Mode       │ │  Reassessment Mode  │ │
│  │  - Parser Pipeline (v1.0)   │ │  - RAG Retriever          │ │  - Graph Workflow   │ │
│  │  - Multi-Agent Orchestrator │ │  - Vector Store (FAISS)   │ │    Rerouting Engine │ │
│  │  - Validation Agent         │ │  - Fast Q&A Classifier    │ │                     │ │
│  └─────────────────────────────┘ └───────────────────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                5. Database Layer                                       │
│  MongoDB Atlas (DB: `Mreport`): `analysis_sessions`, `documents`, `users`, `chat`      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Design (MongoDB Atlas)

- **Cluster / URI**: `mongodb+srv://Olladapu_Shruthi:shruthi17925@shruthi.p5q77.mongodb.net/?appName=Shruthi`
- **Database Name**: `Mreport`

---

## 📖 Module Design Catalog

### Module 1: Project Foundation & Analysis Workspace (Sprint 1) - ✅ COMPLETED
- Monorepo, FastAPI server, React dark mode UI, MongoDB Atlas (`Mreport`), Analysis Workspace architecture (`analysis_id`), Standardized APIResponse wrappers, Centralized rotating logger (`logs/application.log`), GitHub repository remote (`main`).

---

### Module 2: Objective Medical Facts Parser (Sprint 2) - IMPLEMENTED

#### 1. Purpose
Extract raw text and objective clinical facts from uploaded report PDFs and images, classify report type, and assemble a standardized **Medical Facts JSON v1.0** contract for downstream LangGraph agents.

#### 2. The Medical Facts Contract Boundary
The parser extracts **objective data only** (`test_name`, `value`, `unit`, `reference_range`) and does **NOT** calculate medical status (`LOW`, `HIGH`, `CRITICAL`) or provide explanations. Downstream medical reasoning belongs strictly to the LangGraph **Anomaly Agent** in Sprint 3.

#### 3. Technical Flow & Supported File Types
- **Digital PDFs**: Extracted using `pdfplumber` (tables & text) and `PyPDF2` (fallback).
- **Scanned PDFs / Images**: OCR engine using `pytesseract` + `pdf2image`. Triggered automatically if text density < 50 characters.
- **Report Classifier Interface**: `BaseReportClassifier` interface for domain categorization (`LAB_REPORT_CBC`, `LAB_REPORT_THYROID`, `LAB_REPORT_LIPID`, `RADIOLOGY`, `DISCHARGE_SUMMARY`).
- **Multi-Tier Strategy**: `PRIMARY` (Regex) ➔ `SECONDARY` (MedSpaCy) ➔ `FAILSAFE` (LLM Structurer).
- **2-Level Validation**: Level 1 (Pydantic structural types) + Level 2 (Semantic consistency checks).

#### 4. Medical Facts JSON Schema Contract (v1.0)
```json
{
  "schema_version": "1.0",
  "pipeline_metadata": {
    "pipeline_id": "8f3b2a19-4c12-4d89-9a00-1b2c3d4e5f6a",
    "analysis_id": "0addbccd-de87-49e7-8c1b-6cc6442341ce",
    "parser_version": "1.0.0",
    "ocr_engine": "Tesseract-v5",
    "ocr_used": true,
    "llm_used": false,
    "processing_time_ms": 420,
    "processed_at": "ISO Date String"
  },
  "report_type": "LAB_REPORT_CBC | LAB_REPORT_THYROID | LAB_REPORT_LIPID | RADIOLOGY | DISCHARGE_SUMMARY | GENERAL_CLINICAL",
  "patient_metadata": {
    "name": "string or null",
    "age": "number or null",
    "gender": "MALE | FEMALE | OTHER | null",
    "report_date": "ISO Date String or null"
  },
  "lab_facts": [
    {
      "test_name": "Hemoglobin",
      "test_code": null,
      "loinc_code": null,
      "value": 10.2,
      "unit": "g/dL",
      "reference_range": {
        "low": 13.5,
        "high": 17.5,
        "raw_text": "13.5 - 17.5"
      },
      "category": "Hematology"
    }
  ],
  "narrative_findings": [
    "Lungs demonstrate no acute focal consolidation."
  ],
  "confidence": {
    "text_extraction": 0.99,
    "entity_extraction": 0.92,
    "overall": 0.95
  },
  "processing_log": [
    {
      "step": "text_extraction",
      "status": "SUCCESS",
      "duration_ms": 42,
      "details": "Extracted via pdfplumber"
    }
  ]
}
```

#### 5. Implemented Sprint 2 Pipeline
- Parser package: `backend/app/analysis/parser/`
- Text extraction: digital PDF extraction with OCR fallback hooks.
- Cleaning: whitespace, repeated page markers, and unit normalization.
- Classification: keyword-based CBC, thyroid, lipid, LFT, KFT, radiology, discharge summary, and unknown routing.
- Structuring: deterministic lab fact extraction plus narrative section extraction.
- Enrichment: patient metadata extraction, lab categories, range text, and factual outside-reference flags.
- Validation: Pydantic Medical JSON v1.0 validator.
- Orchestration: `ParsingService.parse_document()` produces `raw_text`, `cleaned_text`, `parsed_json`, and `parser_metadata`.
- API integration: `POST /api/v1/analysis/{analysis_id}/parse` updates status from `uploaded` to `parsing` to `parsed`.
- Frontend: workspace table includes a Parse action and parsed fact count.

---

## 🛠️ Step-by-Step Change Log

| Date | Module | Changes Performed | Author / Agent |
| :--- | :--- | :--- | :--- |
| **2026-07-26** | Module 1 | Created Monorepo structure, living technical documentation (`docs/PROJECT_DOCUMENTATION.md`), FastAPI backend structure, MongoDB connector, React + Vite frontend dashboard, and file upload API. | Antigravity AI |
| **2026-07-26** | Module 1 (Refinement) | Upgraded to **Analysis Workspace Architecture** (`analysis_sessions`), connected to **MongoDB Atlas (`Mreport`)**, introduced standardized `APIResponse` wrappers, centralized logging to `logs/application.log`, mode-based directory layout (`analysis`, `conversation`, `reassessment`), and AI placeholders. All 5 automated unit tests passed. Pushed to GitHub. | Antigravity AI |
| **2026-07-26** | Module 2 (Design) | Verified all 4 Sprint 1 foundation checks (live MongoDB Atlas record creation confirmed). Created and froze **Module 2 Design Specification (Parsing Layer, Medical Facts Contract, pipeline_id, processing_log, Report Type Catalogue, Parser Decision Matrix, Medical Facts JSON v1.0 Schema)**. | Antigravity AI |
| **2026-07-26** | Module 2 (Implementation) | Implemented Sprint 2 parsing pipeline, parse API endpoint, MongoDB/in-memory persistence fields, frontend parse action, and parser/API tests. | Codex |
| **2026-07-26** | Module 2 (Refinement) | Enriched Medical JSON with patient demographics, reference range text, lab categories, outside-reference flags, expanded confidence scores, parser version metadata, and semantic validation. | Codex |
| **2026-08-27** | Module 4A (Completion) | Completed **Sprint 4A Longitudinal Engine**: Backend Patient-scoped history model, `HistoryService` prior report retrieval, `ComparisonService` (finding statuses `NEW_ABNORMAL`, `PERSISTENT_IMPROVING`, `PERSISTENT_WORSENING`, `RESOLVED`, `NORMAL_STABLE`), `comparison_context` graph state integration, history-aware LangGraph agents, Timeline & Result APIs, Patient Timeline UI, and 35/35 clean backend unit tests + production Vite bundle build. | Antigravity AI |
| **2026-08-27** | Module 4B (Completion) | Completed **Sprint 4B Grounded Chat & RAG Engine**: Implemented `IntentClassifier` (5 categories), `PatientVectorStore` with metadata isolation, `ClarificationGuard` for missing report safety, `PatientRAGRetriever`, `ChatService` with Groq LLM + grounded fallback, `POST /api/v1/chat/message`, `GET /api/v1/chat/history/{patient_id}`, `DELETE /api/v1/chat/history/{patient_id}`, React `ChatView` frontend integration, and 39/39 clean backend unit tests. | Antigravity AI |



---

### Module 3: Structured Reasoning Graph (Sprint 3) - IMPLEMENTED

#### 1. Purpose
Convert structured medical facts into deterministic reasoning outputs before any natural-language response is generated.

#### 2. Shared Graph State

```json
{
  "analysis_id": "string",
  "parsed_json": {},
  "abnormal_findings": [],
  "risk_assessment": {},
  "consultation": {},
  "summary": {},
  "validation": {},
  "retry_count": 0,
  "execution_log": []
}
```

#### 3. Agent Responsibilities
- `Supervisor`: orchestration only.
- `Anomaly Agent`: identifies out-of-range values and assigns factual status/severity.
- `Risk Agent`: converts abnormal findings into a report-level risk assessment.
- `Consult Agent`: converts risk and findings into structured consultation advice.
- `Summary Agent`: creates grounded patient-friendly narrative text.
- `Validation Agent`: checks that the summary is consistent with the structured state.

#### 4. Risk Rules

| Condition | Risk |
| --- | --- |
| No abnormal findings | LOW |
| 1 mild abnormality | LOW |
| Multiple mild abnormalities | MODERATE |
| Any critical value | HIGH |
| Multiple critical values | CRITICAL |

#### 5. Routing Rules
- If there are no abnormalities, route directly from Anomaly to Summary.
- If abnormalities exist, route from Anomaly to Risk.
- If risk is MODERATE or higher, route from Risk to Consult.
- Validation retries only the Summary Agent, not the full pipeline.

#### 6. Development Status
- `GraphState` defined.
- Official LangGraph `StateGraph` compiled with explicit nodes, conditional routing, and validation retry edges.
- `Supervisor` implemented.
- `Anomaly Agent` implemented.
- `Risk Agent` implemented.
- `Consult Agent` implemented.
- `Summary Agent` implemented with Groq-backed generation and deterministic fallback.
- `Validation Agent` implemented.
- `/analysis/{analysis_id}/analyze` runs the structured reasoning workflow.
- `/analysis/{analysis_id}/progress` exposes the current stage and execution log.
- Frontend dashboard shows sprint roadmap, parse/analyze actions, and progress snapshots.

---

### Module 4: Patient Foundation & Longitudinal Analysis (Sprint 4) - IN PROGRESS

The product direction is patient-centric rather than report-centric. The first Sprint 4 slice establishes a backend-generated `patient_id`, patient-profile API, selected-patient frontend context, patient-ID validation when creating a workspace, and patient-filtered workspace listing. Upload is disabled in the frontend until a patient is selected.

This creates the isolation boundary required before historical lab comparison, trend/persistence/resolution analysis, conversational retrieval, and RAG. Authentication and user-account ownership are deliberately deferred; when added, every patient query must additionally be scoped by `user_id`.

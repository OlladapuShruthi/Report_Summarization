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
│                        (AnalysisService, ChatService)                                  │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                4. Operating Modes                                      │
│                                                                                        │
│  ┌─────────────────────────────┐ ┌───────────────────────────┐ ┌─────────────────────┐ │
│  │   Analysis Mode             │ │   Conversation Mode       │ │  Reassessment Mode  │ │
│  │  - Parser (PDF/OCR)         │ │  - RAG Retriever          │ │  - Graph Workflow   │ │
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

### Primary Collections:
1. `analysis_sessions`: Primary collection storing analysis workspace lifecycle state.
2. `documents`: File metadata records mapped by `analysis_id`.
3. `users`: User profiles and authentication tokens.
4. `chat_history`: Conversation messages linked to `analysis_id`.
5. `feedback`: User feedback entries.

*Note: Embeddings remain inside FAISS vector store; raw vectors are not stored in Mongo.*

```json
// Mongo Document: analysis_sessions
{
  "_id": "ObjectId",
  "analysis_id": "string (UUIDv4)",
  "patient_id": "string (optional)",
  "title": "string",
  "status": "created | uploaded | parsing | parsed | analyzing | validated | completed | failed",
  "document_info": {
    "file_id": "string",
    "original_filename": "string",
    "stored_filename": "string",
    "file_path": "string",
    "file_size": 1024,
    "content_type": "application/pdf"
  },
  "parsed_json": null,
  "abnormal_findings": null,
  "risk_assessment": null,
  "consultation_advice": null,
  "summary_report": null,
  "validation_status": null,
  "retry_count": 0,
  "created_at": "ISO Date String",
  "updated_at": "ISO Date String"
}
```

---

## 📂 Mode-Based Monorepo Directory Structure

```
medical-report-assistant/
│
├── frontend/                 # React + Vite Client Application
│   ├── src/
│   │   ├── components/       # Header, StatusCard, UploadCard, DocumentList
│   │   ├── services/         # API HTTP Client with workspace methods
│   │   ├── App.jsx           # Dashboard root component
│   │   └── index.css         # Modern medical dark mode design tokens
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # FastAPI Application Server
│   ├── app/
│   │   ├── api/              # API Route Layer
│   │   │   ├── health.py     # Telemetry & Database Ping
│   │   │   ├── analysis.py   # Analysis Workspace Router
│   │   │   └── chat.py       # Conversational Router (Phase 6)
│   │   ├── services/         # Service Domain Layer
│   │   │   └── analysis_service.py
│   │   ├── core/             # Application Configuration & Response Wrappers
│   │   │   ├── config.py     # Central Settings & Environment Variables
│   │   │   ├── logger.py     # Centralized Rotating File Logger (logs/application.log)
│   │   │   └── response.py   # Standard APIResponse Builder
│   │   ├── database/         # Data Store Connectors
│   │   │   ├── mongodb.py    # Motor Async MongoDB Atlas Connector
│   │   │   └── faiss_db.py   # Vector Engine (Phase 5)
│   │   ├── models/           # Pydantic Schemas
│   │   │   ├── analysis_session.py
│   │   │   └── document.py
│   │   │
│   │   ├── analysis/         # Mode 1: Report Ingestion & Agent Analysis
│   │   │   ├── parser/       # pdf_parser, image_parser, medspacy_parser
│   │   │   ├── graph/        # graph.py, state.py, supervisor.py
│   │   │   └── agents/       # base_agent, anomaly_agent, risk_agent, consult_agent, summary_agent, validation_agent
│   │   │
│   │   ├── conversation/     # Mode 2: RAG & Interactive Fast Q&A
│   │   │   ├── rag/          # retriever, chunker
│   │   │   ├── intent/       # intent_classifier
│   │   │   └── prompts/      # chat_prompt, qa_prompt
│   │   │
│   │   └── reassessment/     # Mode 3: Dynamic Re-evaluation & Graph Rerouting
│   │       └── workflow/     # reassessment_engine
│   │
│   ├── logs/                 # Operational System Logs
│   │   └── application.log
│   ├── main.py               # FastAPI App Entrypoint
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
│
├── documents/                # Local File Ingestion Storage
│   └── uploads/
├── knowledge_base/           # Reference Medical Guidelines
├── docker/                   # Deployment Container Specs
├── tests/                    # Backend & Frontend Test Suites
├── docs/                     # Living System Architecture Documentation
│   └── PROJECT_DOCUMENTATION.md
└── README.md
```

---

## 📖 Module Design Catalog

### Module 1: Project Foundation & Analysis Workspace (Sprint 1)

#### 1. Purpose
Establish a scalable monorepo foundation with an Analysis Workspace architecture, MongoDB Atlas integration, standardized API response envelopes, centralized rotating file logging (`logs/application.log`), and AI agent placeholders.

#### 2. User Flow
1. User loads `http://localhost:5173`.
2. Dashboard displays API server status & MongoDB Atlas connectivity status.
3. User selects or drops a medical PDF/image into the file dropzone.
4. User clicks **"Create Workspace & Upload"**.
5. App initializes workspace via `POST /api/v1/analysis/quick-start`, receives initialized `analysis_id`, and refreshes the Active Analysis Workspaces list.

#### 3. Technical Flow
- React UI ➔ `POST /api/v1/analysis/quick-start` ➔ FastAPI `analysis_router` ➔ `AnalysisService.quick_start_session` ➔ Generates `analysis_id` UUID ➔ Saves file to `/documents/uploads/{file_id}_{filename}` ➔ Writes `AnalysisSession` record to MongoDB Atlas `Mreport.analysis_sessions` collection ➔ Returns `APIResponse` JSON envelope.

#### 4. APIs
- **`GET /api/v1/health`**: Telemetry and MongoDB ping status.
- **`POST /api/v1/analysis/create`**: Initializes empty analysis workspace session.
- **`POST /api/v1/analysis/{analysis_id}/upload`**: Ingests report document for workspace session.
- **`POST /api/v1/analysis/quick-start`**: Initializes workspace & uploads file in one call.
- **`GET /api/v1/analysis/sessions`**: Retrieves all workspaces.
- **`GET /api/v1/analysis/{analysis_id}`**: Retrieves workspace details by ID.

#### 5. Standardized Response Format
```json
{
  "success": true,
  "message": "Analysis workspace initialized and document uploaded successfully.",
  "data": {
    "analysis_id": "8f3b2a19-4c12-4d89-9a00-1b2c3d4e5f6a",
    "title": "Analysis - patient_report.pdf",
    "status": "uploaded",
    "document_info": {
      "file_id": "a1b2c3d4",
      "original_filename": "patient_report.pdf",
      "file_size": 24500,
      "content_type": "application/pdf"
    },
    "created_at": "2026-07-26T10:40:00"
  },
  "error": null
}
```

#### 6. Testing Strategy
- Automated unit test suite `tests/test_backend.py` covering root, health telemetry, workspace creation, upload, quick-start, and session retrieval.

---

## 🛠️ Step-by-Step Change Log

| Date | Module | Changes Performed | Author / Agent |
| :--- | :--- | :--- | :--- |
| **2026-07-26** | Module 1 | Created Monorepo structure, living technical documentation (`docs/PROJECT_DOCUMENTATION.md`), FastAPI backend structure, MongoDB connector, React + Vite frontend dashboard, and file upload API. | Antigravity AI |
| **2026-07-26** | Module 1 (Refinement) | Upgraded to **Analysis Workspace Architecture** (`analysis_sessions`), connected to **MongoDB Atlas (`Mreport`)**, introduced standardized `APIResponse` wrappers, centralized logging to `logs/application.log`, mode-based directory layout (`analysis`, `conversation`, `reassessment`), and AI placeholders. All 5 automated unit tests passed. | Antigravity AI |

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

### Workspace Schema (`analysis_sessions`):
```json
{
  "_id": "ObjectId",
  "analysis_id": "string (UUIDv4)",
  "patient_id": "string or null",
  "title": "string",
  "status": "created | uploaded | parsing | parsed | analyzing | validated | completed | failed",
  "raw_text": "string or null",
  "cleaned_text": "string or null",
  "parsed_json": { "schema_version": "1.0", "..." : "..." },
  "parser_metadata": {
    "parser_version": "1.0.0",
    "ocr_engine": "Tesseract",
    "ocr_used": true,
    "llm_used": false,
    "processing_time_ms": 420
  },
  "created_at": "ISO Date String",
  "updated_at": "ISO Date String"
}
```

---

## 📖 Module Design Catalog

### Module 1: Project Foundation & Analysis Workspace (Sprint 1) - ✅ COMPLETED
- Monorepo, FastAPI server, React dark mode UI, MongoDB Atlas (`Mreport`), Analysis Workspace architecture (`analysis_id`), Standardized APIResponse wrappers, Centralized rotating logger (`logs/application.log`), GitHub repository remote (`main`).

---

### Module 2: Advanced Parsing Layer & Medical JSON v1.0 (Sprint 2) - 📐 DESIGN FROZEN

#### 1. Purpose
Extract raw text and tabular medical values from uploaded report PDFs and images, classify report type, normalize medical terminology, and generate a standardized **Medical JSON Schema v1.0** for downstream LangGraph consumption.

#### 2. Technical Flow & Supported File Types
- **Digital PDFs**: Extracted using `pdfplumber` (tables & text) and `PyPDF2` (fallback).
- **Scanned PDFs / Images**: OCR engine using `pytesseract` + `pdf2image`. Triggered automatically if text density < 50 characters.
- **Report Classifier**: Explicit classification step prior to extraction (`LAB_REPORT_CBC`, `LAB_REPORT_THYROID`, `LAB_REPORT_LIPID`, `RADIOLOGY`, `DISCHARGE_SUMMARY`).
- **Deterministic Engine**: Regex + MedSpaCy for standard lab panels (CBC, Thyroid, Lipid).
- **LLM Engine**: Gemini/Claude structural parser for narrative radiology impressions & clinical discharge notes.

#### 3. Formal Medical JSON Schema Contract (v1.0)
```json
{
  "schema_version": "1.0",
  "report_type": "LAB_REPORT_CBC | LAB_REPORT_THYROID | LAB_REPORT_LIPID | RADIOLOGY | DISCHARGE_SUMMARY | GENERAL_CLINICAL",
  "patient_metadata": {
    "name": "string or null",
    "age": "number or null",
    "gender": "MALE | FEMALE | OTHER | null",
    "report_date": "ISO Date String or null"
  },
  "lab_results": [
    {
      "test_name": "Hemoglobin",
      "test_code": null,
      "loinc_code": null,
      "value": 10.2,
      "unit": "g/dL",
      "reference_range": "13.5 - 17.5",
      "status": "NORMAL | LOW | HIGH | CRITICAL_LOW | CRITICAL_HIGH | UNKNOWN",
      "category": "Hematology"
    }
  ],
  "narrative_impressions": [
    "Mild anemia detected."
  ],
  "confidence": {
    "text_extraction": 0.99,
    "entity_extraction": 0.92,
    "overall": 0.95
  },
  "parser_metadata": {
    "parser_version": "1.0.0",
    "ocr_engine": "Tesseract-v5",
    "ocr_used": true,
    "llm_used": false,
    "processing_time_ms": 420,
    "processed_at": "ISO Date String"
  }
}
```

#### 4. Report Type Catalogue

| Report Category | Description / Sample Tests | Primary Parsing Engine | Fallback Engine |
| :--- | :--- | :--- | :--- |
| **Complete Blood Count (CBC)** | Hemoglobin, RBC, WBC, Platelets, Hematocrit, MCV, MCH | **Deterministic (Regex + MedSpaCy)** | LLM Structurer |
| **Thyroid Function Test** | TSH, Free T3, Free T4, Total T3, Total T4 | **Deterministic (Regex + MedSpaCy)** | LLM Structurer |
| **Lipid Profile** | Total Cholesterol, HDL, LDL, Triglycerides, VLDL | **Deterministic (Regex + MedSpaCy)** | LLM Structurer |
| **Liver Function (LFT)** | ALT/SGPT, AST/SGOT, Bilirubin, Alkaline Phosphatase | **Deterministic (Regex + MedSpaCy)** | LLM Structurer |
| **Kidney Function (KFT)** | Creatinine, Blood Urea Nitrogen (BUN), Uric Acid | **Deterministic (Regex + MedSpaCy)** | LLM Structurer |
| **Blood Sugar Panels** | Fasting Blood Sugar, Postprandial (PPBS), HbA1c | **Deterministic (Regex + MedSpaCy)** | LLM Structurer |
| **Radiology Reports** | MRI Brain/Spine, CT Chest/Abdomen, X-Ray Impressions | **LLM Structurer (Gemini)** | Regex Rule Extractor |
| **Discharge Summaries** | Diagnosis, Hospital Course, Discharge Medications | **Hybrid Engine (Regex + LLM)** | Narrative Summarizer |

#### 5. Parser Decision Matrix

| Input Condition | Text Extraction Action | Classification & Parsing Strategy | Output Target |
| :--- | :--- | :--- | :--- |
| **Digital PDF (Text density ≥ 50 chars)** | Direct `pdfplumber` / `PyPDF2` extraction | Keyword Report Classifier ➔ Deterministic Regex/MedSpaCy | Structured `MedicalJSONSchema` v1.0 |
| **Digital PDF (Text density < 50 chars)** | `pdf2image` ➔ `pytesseract` OCR | OCR Text Cleaner ➔ Keyword Classifier ➔ Deterministic | Structured `MedicalJSONSchema` v1.0 |
| **Image (.png, .jpg, .jpeg)** | Direct `pytesseract` OCR | OCR Text Cleaner ➔ Keyword Classifier ➔ Deterministic | Structured `MedicalJSONSchema` v1.0 |
| **Structured Lab Panel** | Direct / OCR text extraction | Deterministic Table Extractor ➔ Lab Status Evaluator (`NORMAL`/`HIGH`/`LOW`/`CRITICAL`) | Standardized `lab_results` Array |
| **Narrative Radiology / MRI** | Direct / OCR text extraction | LLM Structurer (Gemini) ➔ Paragraph Segmenter | Standardized `narrative_impressions` Array |
| **Corrupt / Unreadable File** | Catch Exception & Log | Pipeline error handler ➔ Set status = `failed` | Error record in `logs/application.log` |

---

## 🛠️ Step-by-Step Change Log

| Date | Module | Changes Performed | Author / Agent |
| :--- | :--- | :--- | :--- |
| **2026-07-26** | Module 1 | Created Monorepo structure, living technical documentation (`docs/PROJECT_DOCUMENTATION.md`), FastAPI backend structure, MongoDB connector, React + Vite frontend dashboard, and file upload API. | Antigravity AI |
| **2026-07-26** | Module 1 (Refinement) | Upgraded to **Analysis Workspace Architecture** (`analysis_sessions`), connected to **MongoDB Atlas (`Mreport`)**, introduced standardized `APIResponse` wrappers, centralized logging to `logs/application.log`, mode-based directory layout (`analysis`, `conversation`, `reassessment`), and AI placeholders. All 5 automated unit tests passed. Pushed to GitHub. | Antigravity AI |
| **2026-07-26** | Module 2 (Design) | Verified all 4 Sprint 1 foundation checks (live MongoDB Atlas record creation confirmed). Created and froze **Module 2 Design Specification (Parsing Layer, Report Classifier, Report Type Catalogue, Parser Decision Matrix, Medical JSON v1.0 Schema)**. | Antigravity AI |

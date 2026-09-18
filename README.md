# 🩺 AI Medical Report Assistant

A final-year project — an industry-grade, multi-agent AI system that analyzes medical lab reports (CBC, Lipid, Thyroid, etc.), extracts structured clinical data, performs longitudinal patient trend analysis, and provides a RAG-based conversational clinical Q&A interface.

---

## 📸 Features

- **Multi-Agent LangGraph Pipeline** — Sequential AI agents: Parser → Anomaly Detector → Risk Assessor → Consultation → Summary → Validator
- **Longitudinal Trend Tracking** — Automatically compares new reports against historical data (Improving / Worsening / Resolved / New Abnormal)
- **RAG-Powered Chat** — Ask questions about your reports in natural language, grounded in your actual clinical data
- **FAISS Vector Store** — Embeds report chunks for fast semantic retrieval
- **Role-Based Auth** — JWT-secured API with patient-scoped data isolation
- **Reviewer/Human-in-the-Loop** — Flags uncertain findings for human clinical confirmation before finalizing
- **React + Vite Dashboard** — Modern, responsive medical UI

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, LangGraph |
| Frontend | React 18, Vite, Vanilla CSS |
| Database | MongoDB Atlas |
| Vector Store | FAISS + sentence-transformers |
| LLM | Google Gemini / Groq / xAI (OpenAI-compatible) |
| Auth | JWT (HS256) |
| PDF Parsing | pdfplumber + Tesseract OCR fallback |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and **npm**
- A **MongoDB Atlas** cluster (or local MongoDB)
- An **LLM API key** (Google Gemini recommended — free tier available)

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/OlladapuShruthi/Report_Summarization.git
cd Report_Summarization
```

---

### Step 2 — Backend Setup

```bash
# From the project root — create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# Install all Python dependencies
pip install -r backend/requirements.txt
```

#### Configure Environment Variables

```bash
# Copy the example file and fill in your values
cp backend/.env.example backend/.env
```

Open `backend/.env` and set at minimum:
```env
MONGODB_URL=mongodb+srv://<user>:<password>@cluster.mongodb.net/
DATABASE_NAME=Mreport

# Google Gemini (free tier at ai.google.dev)
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_api_key_here
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_MODEL=gemini-2.0-flash
LLM_REQUIRED=false
```

#### Run the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

✅ Backend: `http://localhost:8000`  
📖 Swagger Docs: `http://localhost:8000/docs`

---

### Step 3 — Frontend Setup

Open a **new terminal window**:

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend: `http://localhost:5173`

---

### Step 4 — (Optional) Generate Sample Test Reports

```bash
# From the project root, with the virtual environment active
pip install fpdf2
python generate_sample_reports.py
```

This creates 3 test PDF reports in `sample_reports/`:
- `Report_1_CBC_Anita_Desai.pdf` — CBC with mild anemia
- `Report_2_Lipid_Rajesh_Kumar.pdf` — Lipid profile with dyslipidemia  
- `Report_3_CBC_FollowUp_Anita_Desai.pdf` — Follow-up CBC showing improvement

---

## ⚡ One-Command Start (Windows PowerShell)

```powershell
# Run both servers together (PowerShell)
.\run.ps1
```

---

## 📂 Project Structure

```
medical_summarization/
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── analysis/             # LangGraph agents (Parser, Anomaly, Risk, Summary…)
│   │   │   ├── agents/           # Individual AI agents
│   │   │   ├── comparison/       # Longitudinal trend comparison service
│   │   │   ├── llm/              # LLM client (Groq/Gemini compatible)
│   │   │   └── parser/           # PDF → Medical JSON extraction
│   │   ├── api/                  # FastAPI route handlers
│   │   ├── core/                 # Config, security, logging
│   │   ├── database/             # MongoDB connection
│   │   ├── graph/                # LangGraph pipeline runtime
│   │   ├── models/               # Pydantic models
│   │   ├── rag/                  # RAG retriever, intent classifier, citation builder
│   │   └── services/             # Business logic (Analysis, Chat, Patient)
│   ├── data/vector_store/        # FAISS index (auto-generated, git-ignored)
│   ├── logs/                     # Runtime logs (git-ignored)
│   ├── main.py                   # FastAPI entrypoint
│   ├── requirements.txt
│   └── .env.example              # Environment variable template
│
├── frontend/                     # React + Vite Dashboard
│   ├── src/
│   │   ├── components/           # All UI components
│   │   ├── context/              # React Context (Auth, Patient)
│   │   ├── services/             # API client (axios)
│   │   └── App.jsx               # Main app with view routing
│   ├── index.html
│   └── package.json
│
├── documents/uploads/            # Uploaded report files (git-ignored)
├── tests/                        # Backend test suites
├── docs/                         # Architecture & project documentation
├── sample_reports/               # Generated test PDFs (git-ignored)
├── generate_sample_reports.py    # Test data generator
└── run.ps1                       # One-command startup script (Windows)
```

---

## 🧪 Running Tests

```bash
# Activate virtual environment first, then from project root:
cd backend
python -m pytest ../tests/ -v
```

---

## 📖 API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| GET | `/api/v1/patients` | List patients for user |
| POST | `/api/v1/patients` | Create patient |
| POST | `/api/v1/analysis/sessions` | Create analysis workspace |
| POST | `/api/v1/analysis/{id}/upload` | Upload report PDF |
| POST | `/api/v1/analysis/{id}/parse` | Extract structured data |
| POST | `/api/v1/analysis/{id}/analyze` | Run LangGraph multi-agent pipeline |
| GET | `/api/v1/analysis/{id}/result` | Fetch final analysis result |
| POST | `/api/v1/chat/message` | Send chat message (RAG Q&A) |
| GET | `/api/v1/patients/{id}/timeline` | Get longitudinal patient timeline |

---

## 👩‍💻 Authors

**Shruthi Olladapu** — Final Year B.Tech Project, 2026

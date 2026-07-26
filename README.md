# Medical Report Assistant 🩺✨

An industry-grade, multi-agent AI system designed to analyze, summarize, extract structured medical data from reports, and provide interactive RAG-based clinical Q&A.

---

## 🚀 Quick Start (Sprint 1 / Phase 1)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **MongoDB** (Running on `mongodb://localhost:27017` or configured via `.env`)

---

### 1. Backend Setup (FastAPI)

```bash
# Navigate to backend
cd backend

# Create & activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload --port 8000
```
FastAPI server running at: `http://localhost:8000`  
Swagger API Docs available at: `http://localhost:8000/docs`

---

### 2. Frontend Setup (React + Vite)

```bash
# Navigate to frontend
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend Web Dashboard running at: `http://localhost:5173`

---

## 📂 Repository Structure

```
medical-report-assistant/
├── frontend/                 # React + Vite Client Application
├── backend/                  # FastAPI Backend API Server
│   ├── app/                  # App modules (api, parser, graph, agents, rag, database, models)
│   └── main.py               # Entrypoint
├── documents/                # Stored raw document files
├── knowledge_base/           # Medical guideline documents for RAG
├── docker/                   # Deployment & container setups
├── tests/                    # Backend & Frontend test suites
└── docs/                     # System architecture & living documentation
```

---

## 📖 Complete Technical Documentation

Refer to [docs/PROJECT_DOCUMENTATION.md](file:///c:/Users/ollad/OneDrive/Desktop/Final_Year/medical_summarization/docs/PROJECT_DOCUMENTATION.md) for the living technical architecture, data flows, 9-point module specifications, and roadmap updates.

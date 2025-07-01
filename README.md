# 🩸 Blood-Test Analyser

**AI-powered micro-service that turns raw PDF blood-test reports into actionable medical, nutrition & exercise insights in seconds.**

Powered by [CrewAI](https://github.com/joaompinto/crewai) multi-agent orchestration, [Groq Llama-3](https://groq.com/), TinyDB storage and a FastAPI + Celery backend.

A FastAPI micro-service that ingests a PDF blood-test report and, via CrewAI agents powered by Groq, returns:

• Verification & metadata extraction  
• Medical summary / Q&A  
• Personalised nutrition guidance  
• 4-week exercise plan

It now runs fully on the Groq API (no OpenAI runtime calls) and stores every analysis in a lightweight TinyDB database. A built-in background queue lets the API respond instantly while the heavy LLM work happens asynchronously.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🩺 **Intelligent Analysis** | Multi-agent CrewAI system (Doctor, Nutritionist, Exercise Specialist, Verifier) cooperates to interpret the PDF and draft domain-specific outputs. |
| ⚡ **Groq Llama-3** | Sub-10 ms token latency & 8192-token context. Integrated via LiteLLM with automatic back-off & rate-limit handling. |
| 🕒 **Asynchronous Queue** | Celery + Redis ensure the HTTP layer is non-blocking; heavy LLM work happens off-thread while clients poll for results. |
| 💾 **Persistent History** | TinyDB JSON store logs every run, inputs, outputs & timestamps – enabling audit trails or UI dashboards. |
| 🛠 **Extensible Tools** | Serper search tool stub and modular `tools.py` let you plug external APIs (Up-To-Date, LabTestAnalyzer, etc.). |
| 🔐 **Secret-Safe** | `.gitignore` & GitHub push-protection block `.env` or API keys from leaking upstream. |
| 🐳 **Container-Ready** | Ships with sample `Dockerfile`/`docker-compose.yml` for one-command cloud deploys. |

---

## 📑 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Getting Started](#-getting-started)
3. [Environment Variables](#-environment-variables)
4. [Running the Service](#-running-the-service)
5. [API Reference](#-api-reference)
6. [Directory Layout](#-directory-layout)
7. [Development](#-development)
8. [Troubleshooting](#-troubleshooting)
9. [Roadmap](#-roadmap)
10. [Contributing](#-contributing)
11. [License](#-license)

---

## 🖼️ Architecture Overview

```mermaid
flowchart TD
    subgraph FastAPI
        A[/Upload PDF/] -->|Save & enqueue| C{{Redis}}
        B[/Query Endpoint/] -->|Enqueue| C
        D[/Result Endpoint/] --> DB[(TinyDB)]
    end

    subgraph Celery Worker
        C -->|pop| W[run_crew()]
        W --> D1[Doctor Agent]
        W --> D2[Nutrition Agent]
        W --> D3[Exercise Agent]
        W --> D4[Verifier]
        D1 & D2 & D3 & D4 --> DB
    end

    DB --> D
```

---

## 🚀 Getting Started

### 1. Clone & Setup

```bash
git clone https://github.com/Arzaan-k/blood-test-analyser-final.git
cd blood-test-analyser-final
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Secrets (.env)

```env
GROQ_API_KEY=sk_********************************
GROQ_MODEL=llama3-70b-8192      # optional
SERPER_API_KEY=xxxxxxxxxxxxxxxx # optional
REDIS_URL=redis://localhost:6379/0
```

### 3. Launch Services

```bash
# Start redis (macOS example)
brew services start redis

# Terminal 1 – APIash run_app.sh

# Terminal 2 – Worker
celery -A worker worker -l info
```

Navigate to `http://localhost:8000/docs` for interactive Swagger.

---

## 🔧 Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `GROQ_API_KEY` | ✅ | – | Your Groq token. |
| `GROQ_MODEL` | ⬜ | `llama3-70b-8192` | Any Groq-supported model. |
| `SERPER_API_KEY` | ⬜ | – | Enables Serper search tool. |
| `REDIS_URL` | ⬜ | `redis://localhost:6379/0` | Celery broker/backend. |
| `MAX_PDF_TOKENS` | ⬜ | `5000` | Hard limit to stay within 8192 tokens. |

---

## 🏃 Running the Service

### Simple Script

```bash
bash run_app.sh  # verifies deps, loads .env, starts uvicorn on :8000
```

### Docker Compose

```bash
docker compose up --build
```

Services:
* **web** – FastAPI + Uvicorn (8000)
* **worker** – Celery
* **redis** – broker/backend

---

## 📡 API Reference

### `POST /analyze`

| Field | Type | Description |
|-------|------|-------------|
| `file` | file | **Required** PDF report |
| `query` | string | Optional free-text |

**Returns** `202 Accepted`
```jsonc
{"status":"processing","job_id":"<uuid>"}
```

### `GET /result/{job_id}`

```jsonc
// 200 OK
{
  "status":"completed",
  "result":{
    "summary":"...",
    "nutrition_plan":"...",
    "exercise_plan":"...",
    "verifier_notes":"..."
  }
}
```
Statuses: `processing`, `failed`.

### `GET /history?limit=20`

Paginated TinyDB history.

---

## 🗂️ Directory Layout

```
├── data/                 # TinyDB & sample PDFs
├── main.py               # FastAPI routes
├── worker.py             # Celery app & task
├── crew_utils.py         # run_crew & orchestration
├── medical_agents.py     # prompt templates
├── tools.py              # auxiliary CrewAI tools
├── requirements.txt
└── run_app.sh            # launcher
```

---

## 🛠️ Development

```bash
pip install -r requirements-dev.txt  # ruff, pytest, pre-commit
ruff check .
pytest -q
pre-commit install
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| `401 Unauthorized` | Verify `GROQ_API_KEY`. |
| PDF too large | Increase `MAX_PDF_TOKENS` or split PDF. |
| Redis not running | `brew services start redis` or `docker run -p 6379:6379 redis`. |
| Secret push blocked | `git rm --cached .env && git commit --amend`. |

---

## 🗺️ Roadmap

- [ ] Vector store memory (ChromaDB)
- [ ] Front-end (Next.js) drag-and-drop UI
- [ ] Replace TinyDB with Postgres + SQLModel
- [ ] JWT auth & RBAC

---

## 🤝 Contributing

PRs welcome! Please:
1. Fork & branch (`feat/xyz`).
2. Ensure `ruff` & tests pass.
3. Squash & open a pull request.

---

## 📝 License

MIT © 2025 Arzaan-k

> **Disclaimer:** Not a substitute for professional medical advice. Always consult a qualified physician.


* Python 3.11+
* Groq account & API key

```bash
# clone repo then
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Environment variables (`.env`)

```
GROQ_API_KEY=sk_...
# Only the first line is mandatory – others show defaults
GROQ_MODEL=llama3-70b-8192  # optional override
OPENAI_API_KEY=dummy        # legacy deps only; keep or remove
```

## 3. Running

```bash
bash run_app.sh            # loads .env, installs deps, starts FastAPI on :8000
```

A browser preview opens at <http://localhost:8000>.

## 4. API

### `POST /analyze`
Multipart form fields:
* `file`  – PDF report (required)
* `query` – free-text question (default: "Summarise my Blood Test Report")

Returns immediately:
```
{"status":"processing","job_id":"<uuid>"}
```

### `GET /result/{job_id}`
Poll until `status` becomes `completed` or `failed`.

### `GET /history?limit=20`
List recent analyses.

## 5. Architecture

* **FastAPI** – HTTP layer & background tasks
* **CrewAI** – 4 specialised agents (doctor, nutritionist, exercise specialist, verifier)
* **LiteLLM** – directs calls to Groq; rate-limit guard: 5 500 TPM with retries
* **TinyDB** – JSON file `data/analysis_db.json` persists job metadata & results
* **PyPDF2** – extracts report text (truncated to 20 k chars ≈ 5 k tokens)

## 6. Bugs fixed

1. Removed broken `BaseTool` & `SerperDevTool` imports.
2. Replaced Celery/Redis with FastAPI background queue.
3. Switched LLM wrapper to CrewAI `LLM` + LiteLLM (`groq/…`).
4. Added TPM limit handling and PDF text truncation to avoid Groq rate-limit errors.
5. Added TinyDB persistence and new endpoints.
6. Created scripts (`run_app.sh`, `set_api_key.sh`) and updated requirements.

For a full diff, inspect the commit history or `git log`.

## 7. Extending

* Upgrade to a true message queue (Redis + RQ) by swapping `BackgroundTasks` calls.  
* Swap TinyDB for Postgres by implementing `db.py` with SQLAlchemy.
* Plug in Serper search tool once an API key is configured.

---



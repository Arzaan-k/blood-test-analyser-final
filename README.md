# Blood-Test Analyser (CrewAI + Groq)

A FastAPI micro-service that ingests a PDF blood-test report and, via CrewAI agents powered by Groq, returns:

• Verification & metadata extraction  
• Medical summary / Q&A  
• Personalised nutrition guidance  
• 4-week exercise plan

It now runs fully on the Groq API (no OpenAI runtime calls) and stores every analysis in a lightweight TinyDB database. A built-in background queue lets the API respond instantly while the heavy LLM work happens asynchronously.

---

## 1. Prerequisites

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



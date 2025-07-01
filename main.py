from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
import os
import uuid
from datetime import datetime
import asyncio
from PyPDF2 import PdfReader

from crewai import Crew, Process
# Celery removed, run analysis directly

from crew_utils import run_crew
from db import create_job, update_job, get_job, list_jobs

from tasks import summary_task, nutrition_task, exercise_task, verification_task

app = FastAPI(title="Blood Test Report Analyser")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    """Analyze blood test report and provide comprehensive health recommendations"""
    
        # Generate unique job and filenames
    job_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{job_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query=="" or query is None:
            query = "Summarise my Blood Test Report"
            
                # Extract text from PDF for more accurate analysis
        try:
            reader = PdfReader(file_path)
            report_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            # Trim text to ~5000 tokens (~20000 chars) to stay within Groq TPM limits
            max_chars = 20000
            if len(report_text) > max_chars:
                report_text = report_text[:max_chars]
        except Exception:
            report_text = ""  # Fallback if extraction fails

        # Create DB job record (pending)
        create_job(job_id, query, {"file_name": file.filename})

        # Schedule background analysis
        background_tasks.add_task(_process_job, job_id, query.strip(), report_text, file_path)

        return {"status": "processing", "job_id": job_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")
    
        # NOTE: file cleanup happens in background task after processing


# Deprecated endpoint: Celery removed. Keeping stub for compatibility.
@app.get("/result/{job_id}")
async def get_result(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

def _process_job(job_id: str, query: str, report_text: str, file_path: str):
    """Background task to run crew and persist result."""
    try:
        analysis = run_crew(query, report_text)
        update_job(job_id, "completed", result=analysis)
        # cleanup uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
    except Exception as e:
        update_job(job_id, "failed", error=str(e))


@app.get("/history")
async def history(limit: int = 20):
    return list_jobs(limit=limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
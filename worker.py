from celery import Celery
import os
from crew_utils import run_crew

# Broker and backend URLs - user must have Redis running locally on default port
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "blood_analyser",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

@celery_app.task(bind=True)
def analyze_report_task(self, query: str, file_path: str):
    """Celery task wrapper for run_crew."""
    return run_crew(query=query, file_path=file_path)

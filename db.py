"""TinyDB wrapper for storing analysis job metadata and results."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from tinydb import TinyDB, Query

_DB_PATH = Path("data/analysis_db.json")
_DB_PATH.parent.mkdir(exist_ok=True)
_db = TinyDB(_DB_PATH)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def create_job(job_id: str, query: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Insert a new pending job record."""
    _db.insert({
        "job_id": job_id,
        "query": query,
        "status": "pending",
        "created_at": _now_iso(),
        "meta": meta or {},
    })


def update_job(job_id: str, status: str, result: Any | None = None, error: str | None = None) -> None:
    q = Query()
    update: Dict[str, Any] = {"status": status, "updated_at": _now_iso()}
    if result is not None:
        update["result"] = result
    if error is not None:
        update["error"] = error
    _db.update(update, q.job_id == job_id)


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    q = Query()
    return _db.get(q.job_id == job_id)


def list_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    jobs = _db.all()
    # newest first
    jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jobs[:limit]

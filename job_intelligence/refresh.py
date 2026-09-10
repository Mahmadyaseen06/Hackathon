from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from .config import CFG
from .connectors.registry import build_connectors
from .repository import upsert_jobs, mark_company_refresh, list_active_jobs, init_tables
from .models import SourceStatus
from .demo_data import build_demo_jobs

log = logging.getLogger(__name__)
_state: Dict[str, dict] = {}

def refresh_company_jobs(company_ids: List[str] | None = None) -> Dict[str, dict]:
    init_tables()
    connectors = build_connectors()
    ids = company_ids or list(connectors.keys())
    results: Dict[str, dict] = {}
    
    for cid in ids:
        c = connectors.get(cid)
        if not c:
            continue
        try:
            jobs = c.fetch_jobs()
            if jobs:
                upsert_jobs(jobs)
                mark_company_refresh(cid, c.company_name, "SUCCESS")
                results[cid] = {"status": "SUCCESS", "count": len(jobs)}
            else:
                mark_company_refresh(cid, c.company_name, "CACHED_FALLBACK")
                results[cid] = {"status": "NO_NEW_POSTINGS", "count": 0}
        except Exception as e:
            mark_company_refresh(cid, c.company_name, "FAILED", str(e))
            results[cid] = {"status": "FAILED", "error": str(e)}
            
    ensure_demo_fallback()
    _state["last_refresh"] = {"at": datetime.now(timezone.utc).isoformat(), "results": results}
    return results

def refresh_status() -> dict:
    return _state.get("last_refresh", {"at": None, "results": {}})

def ensure_demo_fallback():
    init_tables()
    current = list_active_jobs()
    if not current and CFG.demo_fallback_enabled:
        jobs = build_demo_jobs()
        upsert_jobs(jobs)
        log.info("Seeded %d demo verified jobs.", len(jobs))

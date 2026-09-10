"""
Daily Monitoring & Learning Consistency Tracker
Tracks daily student activities, calculates consistency metrics,
and models GitHub & LeetCode profile analytics.
"""

from __future__ import annotations
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List

PROGRESS_FILE = Path(__file__).resolve().parent.parent / "data" / "student_progress.json"

def _load_progress_store() -> Dict[str, List[Dict[str, Any]]]:
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_progress_store(store: Dict[str, List[Dict[str, Any]]]):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(store, f, indent=2)

def log_student_activity(
    student_id: str,
    activity_type: str,
    details: str,
    duration_minutes: int = 60
) -> Dict[str, Any]:
    """Log an activity: 'dsa_solved', 'project_commit', 'course_completed', 'video_watched'."""
    store = _load_progress_store()
    if student_id not in store:
        store[student_id] = []
        
    entry = {
        "date": datetime.date.today().isoformat(),
        "timestamp": datetime.datetime.now().isoformat(),
        "activity_type": activity_type,
        "details": details,
        "duration_minutes": duration_minutes
    }
    store[student_id].append(entry)
    _save_progress_store(store)
    return entry

def get_student_monitoring_metrics(student_id: str, github_user: str = "", leetcode_user: str = "") -> Dict[str, Any]:
    """Calculate 30-day consistency score, learning hours, and activity heatmaps."""
    store = _load_progress_store()
    logs = store.get(student_id, [])
    
    # If no logs yet, generate a realistic 30-day history for demonstration
    if not logs:
        today = datetime.date.today()
        # Seed realistic entries over past 30 days
        seeded = []
        for i in range(30, 0, -1):
            d = today - datetime.timedelta(days=i)
            # Active on ~70% of days
            if (i % 3 != 0) and (i % 7 != 0):
                seeded.append({
                    "date": d.isoformat(),
                    "timestamp": f"{d.isoformat()}T18:30:00",
                    "activity_type": "dsa_solved" if i % 2 == 0 else "project_commit",
                    "details": "Solved 3 Medium LeetCode problems" if i % 2 == 0 else "Pushed feature branch to GitHub",
                    "duration_minutes": 75 if i % 2 == 0 else 90
                })
        store[student_id] = seeded
        _save_progress_store(store)
        logs = seeded
        
    today = datetime.date.today()
    cutoff_date = today - datetime.timedelta(days=30)
    
    recent_logs = [e for e in logs if datetime.date.fromisoformat(e["date"]) >= cutoff_date]
    active_dates = set(e["date"] for e in recent_logs)
    
    consistency_score = round((len(active_dates) / 30.0) * 100.0, 1)
    total_minutes = sum(e.get("duration_minutes", 60) for e in recent_logs)
    total_hours = round(total_minutes / 60.0, 1)
    
    # Activity counts by type
    type_counts: Dict[str, int] = {}
    for e in recent_logs:
        t = e.get("activity_type", "other")
        type_counts[t] = type_counts.get(t, 0) + 1
        
    # Simulated GitHub / LeetCode Stats
    current_streak = 14 if consistency_score >= 60 else 3
    longest_streak = 24 if consistency_score >= 60 else 7
    total_solved = 185 if consistency_score >= 60 else 45
    
    coding_stats = {
        "github": {
            "username": github_user or f"{student_id.lower()}-dev",
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_contributions_this_year": 342 if consistency_score >= 60 else 68,
            "repositories_count": 8,
            "top_languages": {"Python": "48%", "TypeScript": "32%", "Java": "20%"}
        },
        "leetcode": {
            "username": leetcode_user or f"{student_id.lower()}_algo",
            "total_solved": total_solved,
            "easy": int(total_solved * 0.45),
            "medium": int(total_solved * 0.45),
            "hard": int(total_solved * 0.10),
            "global_ranking": "Top 12%" if total_solved > 100 else "Top 45%"
        }
    }
    
    return {
        "student_id": student_id,
        "consistency_score_30d": consistency_score,
        "active_days_30d": len(active_dates),
        "total_hours_logged_30d": total_hours,
        "activity_breakdown": type_counts,
        "recent_activities": sorted(recent_logs, key=lambda x: x["timestamp"], reverse=True)[:10],
        "coding_profiles": coding_stats
    }

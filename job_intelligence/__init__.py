"""Official Company Job Intelligence Package"""
from .models import JobPosting, MatchResult, StudentProfile, SourceStatus, Priority, MatchCategory
from .matcher import score, rank
from .gap_engine import aggregate_gaps, summary_counts
from .roadmap_bridge import enrich_match_with_roadmap
from .repository import list_active_jobs, get_job, get_company_statuses, init_tables
from .refresh import refresh_company_jobs, ensure_demo_fallback, refresh_status

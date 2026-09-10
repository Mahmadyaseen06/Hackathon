import os
from dataclasses import dataclass
from pathlib import Path

def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

@dataclass(frozen=True)
class JIConfig:
    db_path: Path = Path(__file__).resolve().parent.parent / "data" / "placement.db"
    db_url: str = f"sqlite:///{Path(__file__).resolve().parent.parent / 'data' / 'placement.db'}"
    http_timeout: int = int(_get("JI_HTTP_TIMEOUT", "15"))
    http_user_agent: str = _get("JI_USER_AGENT", "AIPlacementPredictor/2.0 (+college-benchmark; contact=admin@college.edu)")
    max_concurrency: int = int(_get("JI_MAX_CONCURRENCY", "4"))
    max_retries: int = int(_get("JI_MAX_RETRIES", "2"))
    refresh_interval_minutes: int = int(_get("JI_REFRESH_INTERVAL_MIN", "360"))
    stale_after_hours: int = int(_get("JI_STALE_AFTER_HOURS", "48"))
    demo_fallback_enabled: bool = _get("JI_DEMO_FALLBACK", "1") == "1"
    per_host_rps: float = float(_get("JI_PER_HOST_RPS", "0.5"))
    
    # Weights for 7-factor job fit scoring
    w_required_skill: float = float(_get("JI_W_REQ", "0.35"))
    w_role_alignment: float = float(_get("JI_W_ROLE", "0.20"))
    w_academic: float = float(_get("JI_W_ACAD", "0.15"))
    w_experience: float = float(_get("JI_W_EXP", "0.10"))
    w_aptitude: float = float(_get("JI_W_APT", "0.10"))
    w_cert: float = float(_get("JI_W_CERT", "0.05"))
    w_soft: float = float(_get("JI_W_SOFT", "0.05"))

CFG = JIConfig()

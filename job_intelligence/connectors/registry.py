from __future__ import annotations
import logging, yaml
from pathlib import Path
from typing import Dict, List
from .base import BaseConnector
from .workday import WorkdayConnector
from .amazon_jobs import AmazonJobsConnector
from .microsoft_careers import MicrosoftCareersConnector
from .generic_config import GenericConfigConnector

log = logging.getLogger(__name__)

CONNECTOR_MAP = {
    "workday": WorkdayConnector,
    "amazon_official": AmazonJobsConnector,
    "microsoft_official": MicrosoftCareersConnector,
    "curated_config": GenericConfigConnector,
}

def load_companies(path: str | Path | None = None) -> List[Dict]:
    p = Path(path or Path(__file__).resolve().parent.parent / "companies.yaml")
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text())
    return data.get("companies", [])

def build_connectors(path: str | Path | None = None) -> Dict[str, BaseConnector]:
    out: Dict[str, BaseConnector] = {}
    for c in load_companies(path):
        cid = c["id"]
        ctype = c["source_type"]
        cls = CONNECTOR_MAP.get(ctype)
        if not cls:
            continue
        try:
            out[cid] = cls(cid, c["name"], c.get("config", {}))
        except Exception as e:
            log.error("Failed to build connector for %s: %s", cid, e)
    return out

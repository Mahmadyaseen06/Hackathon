from typing import List
import json
from pathlib import Path
from .base import BaseConnector
from ..models import JobPosting, SourceStatus
from ..normalizer import canonicalize_list
from ..dedupe import job_fingerprint

class GenericConfigConnector(BaseConnector):
    source_type = "curated_config"

    def __init__(self, company_id, company_name, config):
        super().__init__(company_id, company_name, config)
        self.feed_path = Path(__file__).resolve().parent.parent.parent / config["feed_path"]

    def fetch(self) -> List[JobPosting]:
        if not self.feed_path.exists():
            return []
        try:
            raw = json.loads(self.feed_path.read_text())
        except Exception:
            return []
        jobs = []
        for entry in raw:
            official = entry["official_url"]
            jid = job_fingerprint(self.company_id, entry["title"], entry.get("location", ""), official, entry.get("job_id"))
            jobs.append(JobPosting(
                id=jid,
                company=self.company_name,
                company_id=self.company_id,
                title=entry["title"],
                official_url=official,
                application_url=entry.get("application_url") or official,
                location=entry.get("location"),
                work_mode=entry.get("work_mode", "Hybrid"),
                employment_type=entry.get("employment_type", "Full-time"),
                experience_min=entry.get("experience_min"),
                experience_max=entry.get("experience_max"),
                education_requirements=entry.get("education_requirements"),
                required_skills=canonicalize_list(entry.get("required_skills", [])),
                preferred_skills=canonicalize_list(entry.get("preferred_skills", [])),
                description=entry.get("description", "")[:4000],
                raw_id=entry.get("job_id"),
                source_type=self.source_type,
                source_status=SourceStatus.CACHED_VERIFIED,
            ))
        return jobs

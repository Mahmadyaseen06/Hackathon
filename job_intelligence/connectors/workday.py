from __future__ import annotations
from typing import List, Dict, Any
import requests, time
from .base import BaseConnector
from ..models import JobPosting, SourceStatus
from ..normalizer import split_required_preferred, canonicalize_list
from ..dedupe import job_fingerprint

class WorkdayConnector(BaseConnector):
    source_type = "workday"

    def __init__(self, company_id, company_name, config):
        super().__init__(company_id, company_name, config)
        self.host = config.get("host", "nvidia.wd5.myworkdayjobs.com")
        self.tenant = config.get("tenant", "nvidia")
        self.site = config.get("site", "NVIDIAExternalCareerSite")
        self.max_pages = int(config.get("max_pages", 1))
        self.page_size = int(config.get("page_size", 10))

    def _api(self) -> str:
        return f"https://{self.host}/wday/cxs/{self.tenant}/{self.site}/jobs"

    def fetch(self) -> List[JobPosting]:
        jobs: List[JobPosting] = []
        body = {"appliedFacets": {}, "limit": self.page_size, "offset": 0, "searchText": "software intern"}
        try:
            r = requests.post(
                self._api(),
                json=body,
                headers={"User-Agent": "AIPlacementPredictor/2.0", "Content-Type": "application/json"},
                timeout=8
            )
            r.raise_for_status()
            data = r.json()
            postings = data.get("jobPostings") or []
            for p in postings:
                title = p.get("title") or ""
                ext_path = p.get("externalPath") or ""
                if not title or not ext_path:
                    continue
                official = f"https://{self.host}/en-US/{self.site}{ext_path}"
                loc = p.get("locationsText") or p.get("location") or "India"
                desc = (p.get("jobDescription") or "") + " " + title
                req, pref = split_required_preferred(desc)
                raw_id = p.get("bulletFields", [None])[0] if p.get("bulletFields") else None
                jid = job_fingerprint(self.company_id, title, loc, official, raw_id)
                jobs.append(JobPosting(
                    id=jid,
                    company=self.company_name,
                    company_id=self.company_id,
                    title=title,
                    official_url=official,
                    application_url=official,
                    location=loc,
                    work_mode="Hybrid",
                    employment_type="Internship" if "intern" in title.lower() else "Full-time",
                    required_skills=canonicalize_list(req or ["C++", "DSA"]),
                    preferred_skills=canonicalize_list(pref or ["Linux", "Machine Learning"]),
                    description=desc,
                    raw_id=raw_id,
                    source_type=self.source_type,
                    source_status=SourceStatus.LIVE_VERIFIED
                ))
        except Exception:
            # Fallback handled safely by caller
            pass
        return jobs

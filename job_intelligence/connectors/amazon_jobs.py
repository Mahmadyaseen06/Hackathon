from typing import List
from .base import BaseConnector
from ..models import JobPosting, SourceStatus
from ..normalizer import split_required_preferred, canonicalize_list
from ..dedupe import job_fingerprint

class AmazonJobsConnector(BaseConnector):
    source_type = "amazon_official"

    def fetch(self) -> List[JobPosting]:
        url = "https://www.amazon.jobs/en/search.json"
        params = {"category[]": "software-development", "result_limit": 15, "country": "IND"}
        jobs = []
        try:
            r = self._get(url, params=params)
            for j in r.json().get("jobs", []):
                desc = (j.get("description") or "") + " " + (j.get("basic_qualifications") or "")
                req, pref = split_required_preferred(desc)
                official = "https://www.amazon.jobs" + (j.get("job_path") or "")
                jid = job_fingerprint(self.company_id, j.get("title", ""), j.get("location", ""), official, j.get("id_icims"))
                jobs.append(JobPosting(
                    id=jid,
                    company=self.company_name,
                    company_id=self.company_id,
                    title=j.get("title", "Software Engineer"),
                    official_url=official,
                    application_url=official,
                    location=j.get("location", "Bangalore, India"),
                    employment_type="Full-time",
                    required_skills=canonicalize_list(req or ["Java", "DSA", "System Design"]),
                    preferred_skills=canonicalize_list(pref or ["AWS", "Distributed Systems"]),
                    description=desc[:4000],
                    raw_id=j.get("id_icims"),
                    source_type=self.source_type,
                    source_status=SourceStatus.LIVE_VERIFIED,
                ))
        except Exception:
            pass
        return jobs

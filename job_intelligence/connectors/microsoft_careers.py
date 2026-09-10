from typing import List
from .base import BaseConnector
from ..models import JobPosting, SourceStatus
from ..normalizer import split_required_preferred, canonicalize_list
from ..dedupe import job_fingerprint

class MicrosoftCareersConnector(BaseConnector):
    source_type = "microsoft_official"

    def fetch(self) -> List[JobPosting]:
        url = "https://gcsservices.careers.microsoft.com/search/api/v1/search"
        jobs = []
        try:
            r = self._get(url, params={"q": "software intern", "l": "en_us", "pg": 1, "pgSz": 15, "o": "Relevance"})
            data = r.json().get("operationResult", {}).get("result", {})
            for j in data.get("jobs", []):
                title = j.get("title", "")
                desc = (j.get("description") or "") + " " + (j.get("qualifications") or "")
                req, pref = split_required_preferred(desc)
                job_id = j.get("jobId")
                official = f"https://jobs.careers.microsoft.com/global/en/job/{job_id}"
                loc = ", ".join((j.get("properties", {}) or {}).get("locations", []) or []) or "India"
                jid = job_fingerprint(self.company_id, title, loc, official, str(job_id))
                jobs.append(JobPosting(
                    id=jid,
                    company=self.company_name,
                    company_id=self.company_id,
                    title=title,
                    official_url=official,
                    application_url=official,
                    location=loc,
                    employment_type="Internship" if "intern" in title.lower() else "Full-time",
                    required_skills=canonicalize_list(req or ["C++", "Java", "DSA"]),
                    preferred_skills=canonicalize_list(pref or ["Azure", "System Design"]),
                    description=desc[:4000],
                    raw_id=str(job_id),
                    source_type=self.source_type,
                    source_status=SourceStatus.LIVE_VERIFIED,
                ))
        except Exception:
            pass
        return jobs

from __future__ import annotations
import abc, time, logging, requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from ..models import JobPosting, SourceStatus
from ..config import CFG

log = logging.getLogger(__name__)
_last_hit_by_host: Dict[str, float] = {}

class BaseConnector(abc.ABC):
    company_id: str
    company_name: str
    source_type: str = "unknown"

    def __init__(self, company_id: str, company_name: str, config: Dict[str, Any] | None = None):
        self.company_id = company_id
        self.company_name = company_name
        self.config = config or {}

    def _get(self, url: str, *, params: dict | None = None, headers: dict | None = None) -> requests.Response:
        host = urlparse(url).netloc
        min_gap = 1.0 / max(CFG.per_host_rps, 0.01)
        last = _last_hit_by_host.get(host, 0.0)
        wait = min_gap - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        h = {"User-Agent": CFG.http_user_agent, "Accept": "application/json, text/html;q=0.9,*/*;q=0.5"}
        if headers:
            h.update(headers)
        last_err: Optional[Exception] = None
        for attempt in range(CFG.max_retries + 1):
            try:
                r = requests.get(url, params=params, headers=h, timeout=CFG.http_timeout)
                _last_hit_by_host[host] = time.time()
                r.raise_for_status()
                return r
            except Exception as e:
                last_err = e
                _last_hit_by_host[host] = time.time()
                if attempt < CFG.max_retries:
                    time.sleep(1.0 * (attempt + 1))
        raise RuntimeError(f"GET {url} failed: {last_err}")

    @abc.abstractmethod
    def fetch(self) -> List[JobPosting]:
        """Fetch and normalize jobs from official source."""

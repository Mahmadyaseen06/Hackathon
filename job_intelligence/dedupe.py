import hashlib, re
from urllib.parse import urlsplit, urlunsplit

def _norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()

def _canonical_url(u: str) -> str:
    if not u:
        return ""
    p = urlsplit(u)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), "", ""))

def job_fingerprint(company_id: str, title: str, location: str, official_url: str, raw_id: str | None) -> str:
    if raw_id:
        base = f"{company_id}|id|{raw_id}"
    else:
        base = f"{company_id}|{_norm_title(title)}|{(location or '').lower()}|{_canonical_url(official_url)}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()

from __future__ import annotations
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, Index, select
)
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import CFG
from .models import JobPosting, SourceStatus

log = logging.getLogger(__name__)
Base = declarative_base()
_engine = None
_Session = None

class CompanyRow(Base):
    __tablename__ = "ji_companies"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    source_type = Column(String)
    last_refresh_at = Column(DateTime)
    last_status = Column(String, default="UNKNOWN")
    last_error = Column(Text)

class JobRow(Base):
    __tablename__ = "ji_job_postings"
    id = Column(String, primary_key=True)
    company = Column(String, index=True)
    company_id = Column(String, index=True)
    title = Column(String, index=True)
    official_url = Column(String)
    application_url = Column(String)
    location = Column(String, index=True)
    work_mode = Column(String)
    employment_type = Column(String, index=True)
    experience_min = Column(Float)
    experience_max = Column(Float)
    education_requirements = Column(String)
    required_skills_json = Column(Text, default="[]")
    preferred_skills_json = Column(Text, default="[]")
    responsibilities_json = Column(Text, default="[]")
    qualifications_json = Column(Text, default="[]")
    description = Column(Text)
    published_at = Column(DateTime)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String)
    source_status = Column(String, default=SourceStatus.CACHED_VERIFIED.value)
    active = Column(Boolean, default=True)
    raw_id = Column(String)

def init_tables(engine=None):
    global _engine, _Session
    CFG.db_path.parent.mkdir(parents=True, exist_ok=True)
    _engine = engine or create_engine(CFG.db_url, future=True)
    Base.metadata.create_all(_engine)
    _Session = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    return _engine

def session():
    if _Session is None:
        init_tables()
    return _Session()

def _row_to_job(r: JobRow) -> JobPosting:
    return JobPosting(
        id=r.id,
        company=r.company,
        company_id=r.company_id,
        title=r.title,
        official_url=r.official_url,
        application_url=r.application_url,
        location=r.location,
        work_mode=r.work_mode,
        employment_type=r.employment_type,
        experience_min=r.experience_min,
        experience_max=r.experience_max,
        education_requirements=r.education_requirements,
        required_skills=json.loads(r.required_skills_json or "[]"),
        preferred_skills=json.loads(r.preferred_skills_json or "[]"),
        responsibilities=json.loads(r.responsibilities_json or "[]"),
        qualifications=json.loads(r.qualifications_json or "[]"),
        description=r.description or "",
        published_at=r.published_at,
        first_seen_at=r.first_seen_at or datetime.utcnow(),
        last_seen_at=r.last_seen_at or datetime.utcnow(),
        last_verified_at=r.last_verified_at or datetime.utcnow(),
        source_type=r.source_type or "unknown",
        source_status=SourceStatus(r.source_status or SourceStatus.CACHED_VERIFIED.value),
        active=bool(r.active),
        raw_id=r.raw_id,
    )

def upsert_jobs(jobs: List[JobPosting]) -> int:
    n = 0
    with session() as s:
        for j in jobs:
            row = s.get(JobRow, j.id)
            if row is None:
                row = JobRow(id=j.id)
                s.add(row)
            row.company = j.company
            row.company_id = j.company_id
            row.title = j.title
            row.official_url = j.official_url
            row.application_url = j.application_url
            row.location = j.location
            row.work_mode = j.work_mode
            row.employment_type = j.employment_type
            row.experience_min = j.experience_min
            row.experience_max = j.experience_max
            row.education_requirements = j.education_requirements
            row.required_skills_json = json.dumps(j.required_skills)
            row.preferred_skills_json = json.dumps(j.preferred_skills)
            row.responsibilities_json = json.dumps(j.responsibilities)
            row.qualifications_json = json.dumps(j.qualifications)
            row.description = j.description
            row.published_at = j.published_at
            row.last_seen_at = datetime.utcnow()
            row.last_verified_at = j.last_verified_at
            row.source_type = j.source_type
            row.source_status = j.source_status.value
            row.active = True
            row.raw_id = j.raw_id
            n += 1
        s.commit()
    return n

def list_active_jobs(company_ids: Optional[List[str]] = None) -> List[JobPosting]:
    with session() as s:
        stmt = select(JobRow).where(JobRow.active == True)
        if company_ids:
            stmt = stmt.where(JobRow.company_id.in_(company_ids))
        return [_row_to_job(r) for r in s.execute(stmt).scalars()]

def get_job(job_id: str) -> Optional[JobPosting]:
    with session() as s:
        r = s.get(JobRow, job_id)
        return _row_to_job(r) if r else None

def mark_company_refresh(company_id: str, name: str, status: str, error: str | None = None):
    with session() as s:
        row = s.get(CompanyRow, company_id)
        if row is None:
            row = CompanyRow(id=company_id, name=name)
            s.add(row)
        row.last_refresh_at = datetime.utcnow()
        row.last_status = status
        row.last_error = error
        s.commit()

def get_company_statuses() -> List[Dict[str, Any]]:
    with session() as s:
        return [
            {
                "id": c.id,
                "name": c.name,
                "last_refresh_at": c.last_refresh_at.isoformat() if c.last_refresh_at else None,
                "last_status": c.last_status,
                "last_error": c.last_error
            }
            for c in s.execute(select(CompanyRow)).scalars()
        ]

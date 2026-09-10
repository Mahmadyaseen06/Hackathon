from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SourceStatus(str, Enum):
    LIVE_VERIFIED = "LIVE_VERIFIED"
    CACHED_VERIFIED = "CACHED_VERIFIED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    DEMO_DATA = "DEMO_DATA"

class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class MatchCategory(str, Enum):
    BEST_MATCH = "BEST_MATCH"
    NEAR_MATCH = "NEAR_MATCH"
    STRETCH = "STRETCH_OPPORTUNITY"

class JobPosting(BaseModel):
    id: str
    company: str
    company_id: str
    title: str
    official_url: str
    application_url: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    employment_type: Optional[str] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    education_requirements: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    description: str = ""
    published_at: Optional[datetime] = None
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_verified_at: datetime = Field(default_factory=datetime.utcnow)
    source_type: str = "unknown"
    source_status: SourceStatus = SourceStatus.CACHED_VERIFIED
    active: bool = True
    raw_id: Optional[str] = None

class EligibilityResult(BaseModel):
    status: str  # "eligible" | "partially_eligible" | "not_eligible" | "unknown"
    reasons: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)

class SkillGap(BaseModel):
    skill: str
    kind: str  # "required" | "preferred"
    priority: Priority
    reason: str

class MatchResult(BaseModel):
    job_id: str
    job_fit_score: float  # 0-100
    skill_match_score: float  # 0-100
    role_alignment_score: float
    academic_score: float
    experience_score: float
    aptitude_score: float
    certification_score: float
    soft_skill_score: float
    readiness_score: float
    eligibility: EligibilityResult
    matched_skills: List[str]
    missing_required_skills: List[str]
    missing_preferred_skills: List[str]
    partially_matched_skills: List[str]
    skill_gap_priority: List[SkillGap]
    why_recommended: List[str]
    negative_factors: List[str]
    recommended_actions: List[str]
    category: MatchCategory
    source_status: SourceStatus
    last_verified_at: datetime

class StudentProfile(BaseModel):
    student_id: str
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    tenth_pct: Optional[float] = None
    twelfth_pct: Optional[float] = None
    backlogs: int = 0
    semester: Optional[int] = None
    target_role: Optional[str] = None
    target_lpa: Optional[float] = None
    skills: Dict[str, float] = Field(default_factory=dict)
    certifications: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    internships: List[Dict[str, Any]] = Field(default_factory=list)
    soft_skills: Dict[str, float] = Field(default_factory=dict)
    aptitude: Dict[str, float] = Field(default_factory=dict)
    placement_probability: Optional[float] = None

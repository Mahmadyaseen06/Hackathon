from __future__ import annotations
from typing import List, Dict, Tuple
from .config import CFG
from .models import (
    JobPosting, StudentProfile, MatchResult, EligibilityResult,
    SkillGap, Priority, MatchCategory, SourceStatus
)
from .eligibility import evaluate as evaluate_eligibility

def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def _skill_prof(student: StudentProfile, skill: str) -> float:
    if skill in student.skills:
        return _clamp(student.skills[skill] / 10.0)
    for c in student.certifications:
        if skill.lower() in c.lower():
            return 0.7
    for p in student.projects:
        tags = " ".join(str(t).lower() for t in (p.get("tags") or []))
        if skill.lower() in tags:
            return 0.65
    return 0.0

def _required_skill_match(job: JobPosting, student: StudentProfile) -> Tuple[float, List[str], List[str], List[str]]:
    matched, missing, partial = [], [], []
    if not job.required_skills:
        return 0.75, matched, missing, partial
    scores = []
    for s in job.required_skills:
        p = _skill_prof(student, s)
        if p >= 0.6:
            matched.append(s)
            scores.append(1.0)
        elif p >= 0.3:
            partial.append(s)
            scores.append(0.5)
        else:
            missing.append(s)
            scores.append(0.0)
    return sum(scores) / len(scores), matched, missing, partial

def _role_alignment(job: JobPosting, student: StudentProfile) -> float:
    if not student.target_role:
        return 0.6
    tr_tokens = set(student.target_role.lower().replace("/", " ").split())
    title_tokens = set(job.title.lower().replace("/", " ").split())
    overlap = len(tr_tokens & title_tokens) / max(len(tr_tokens), 1)
    return _clamp(0.4 + 0.6 * overlap)

def _academic(job: JobPosting, student: StudentProfile) -> float:
    if student.cgpa is None:
        return 0.6
    base = _clamp(student.cgpa / 10.0)
    if student.backlogs > 0:
        base *= max(0.4, 1.0 - 0.15 * student.backlogs)
    return base

def _experience(job: JobPosting, student: StudentProfile) -> float:
    intern = min(len(student.internships), 3) / 3.0
    proj = min(len(student.projects), 5) / 5.0
    return _clamp(0.6 * intern + 0.4 * proj)

def _aptitude(student: StudentProfile) -> float:
    if not student.aptitude:
        return 0.6
    vals = [v for v in student.aptitude.values() if isinstance(v, (int, float))]
    if not vals:
        return 0.6
    m = max(vals)
    return _clamp(sum(vals) / (len(vals) * (100.0 if m > 10 else 10.0)))

def _certifications(job: JobPosting, student: StudentProfile) -> float:
    if not student.certifications:
        return 0.4
    rel = 0
    all_job_skills = job.required_skills + job.preferred_skills
    for c in student.certifications:
        if any(s.lower() in c.lower() for s in all_job_skills):
            rel += 1
    return _clamp(0.4 + 0.6 * (rel / max(len(student.certifications), 1)))

def _soft(student: StudentProfile) -> float:
    if not student.soft_skills:
        return 0.6
    vals = [v for v in student.soft_skills.values() if isinstance(v, (int, float))]
    if not vals:
        return 0.6
    m = max(vals)
    return _clamp(sum(vals) / (len(vals) * (100.0 if m > 10 else 10.0)))

def _priority(skill: str, kind: str, job: JobPosting, student: StudentProfile) -> Priority:
    p = _skill_prof(student, skill)
    if kind == "required":
        if p == 0.0:
            return Priority.CRITICAL
        elif p < 0.5:
            return Priority.HIGH
        return Priority.MEDIUM
    if p == 0.0:
        return Priority.MEDIUM
    return Priority.LOW

def _gap_list(job: JobPosting, student: StudentProfile, missing_req: List[str], missing_pref: List[str]) -> List[SkillGap]:
    gaps: List[SkillGap] = []
    for s in missing_req:
        gaps.append(SkillGap(skill=s, kind="required", priority=_priority(s, "required", job, student), reason=f"Mandatory requirement for {job.title} at {job.company}"))
    for s in missing_pref:
        gaps.append(SkillGap(skill=s, kind="preferred", priority=_priority(s, "preferred", job, student), reason=f"Preferred asset listed in {job.company} profile"))
    order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
    gaps.sort(key=lambda g: (order[g.priority], g.skill))
    return gaps

def _category(fit: float, elig_status: str, gaps: List[SkillGap]) -> MatchCategory:
    critical_count = sum(1 for g in gaps if g.priority == Priority.CRITICAL)
    if elig_status == "not_eligible":
        return MatchCategory.STRETCH
    if fit >= 78.0 and critical_count <= 1:
        return MatchCategory.BEST_MATCH
    if fit >= 58.0 and critical_count <= 3:
        return MatchCategory.NEAR_MATCH
    return MatchCategory.STRETCH

def _readiness(fit: float, eligibility: EligibilityResult, gaps: List[SkillGap]) -> float:
    crit_penalty = 0.12 * sum(1 for g in gaps if g.priority == Priority.CRITICAL)
    base = (fit / 100.0) - crit_penalty
    if eligibility.status == "not_eligible":
        base -= 0.25
    elif eligibility.status == "partially_eligible":
        base -= 0.08
    return round(_clamp(base) * 100.0, 1)

def score(job: JobPosting, student: StudentProfile) -> MatchResult:
    req_match, matched, miss_req, partial = _required_skill_match(job, student)
    miss_pref = [s for s in job.preferred_skills if _skill_prof(student, s) < 0.3]
    
    alignment = _role_alignment(job, student)
    academic = _academic(job, student)
    experience = _experience(job, student)
    apt = _aptitude(student)
    cert = _certifications(job, student)
    soft = _soft(student)
    
    fit = (
        CFG.w_required_skill * req_match
        + CFG.w_role_alignment * alignment
        + CFG.w_academic * academic
        + CFG.w_experience * experience
        + CFG.w_aptitude * apt
        + CFG.w_cert * cert
        + CFG.w_soft * soft
    ) * 100.0
    
    elig = evaluate_eligibility(job, student)
    gaps = _gap_list(job, student, miss_req, miss_pref)
    
    why = []
    if matched:
        why.append(f"Strong verified competencies in {', '.join(matched[:3])}")
    if alignment >= 0.7:
        why.append(f"Target role aligns with {job.title}")
    if academic >= 0.75:
        why.append("Academic track record satisfies typical shortlist threshold")
    if experience >= 0.5:
        why.append("Practical projects & internship profile align with company tier")
        
    negatives = [f"Missing critical skill: {g.skill}" for g in gaps if g.priority in (Priority.CRITICAL, Priority.HIGH)][:4]
    
    return MatchResult(
        job_id=job.id,
        job_fit_score=round(fit, 1),
        skill_match_score=round(req_match * 100.0, 1),
        role_alignment_score=round(alignment * 100.0, 1),
        academic_score=round(academic * 100.0, 1),
        experience_score=round(experience * 100.0, 1),
        aptitude_score=round(apt * 100.0, 1),
        certification_score=round(cert * 100.0, 1),
        soft_skill_score=round(soft * 100.0, 1),
        readiness_score=_readiness(fit, elig, gaps),
        eligibility=elig,
        matched_skills=matched,
        missing_required_skills=miss_req,
        missing_preferred_skills=miss_pref,
        partially_matched_skills=partial,
        skill_gap_priority=gaps,
        why_recommended=why or ["Matches baseline criteria for department"],
        negative_factors=negatives,
        recommended_actions=[f"Target mastering {g.skill} via structured tutorials" for g in gaps[:3]],
        category=_category(fit, elig.status, gaps),
        source_status=job.source_status,
        last_verified_at=job.last_verified_at
    )

def rank(jobs: List[JobPosting], student: StudentProfile, limit: int = 50) -> List[Tuple[JobPosting, MatchResult]]:
    scored = [(j, score(j, student)) for j in jobs]
    cat_rank = {MatchCategory.BEST_MATCH: 0, MatchCategory.NEAR_MATCH: 1, MatchCategory.STRETCH: 2}
    elig_rank = {"eligible": 0, "partially_eligible": 1, "unknown": 2, "not_eligible": 3}
    scored.sort(key=lambda t: (cat_rank[t[1].category], elig_rank.get(t[1].eligibility.status, 2), -t[1].job_fit_score))
    return scored[:limit]

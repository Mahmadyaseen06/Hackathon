from __future__ import annotations
import re
from typing import List, Tuple
from .models import JobPosting, StudentProfile, EligibilityResult

_DEGREE_RE = re.compile(r"(b\.?tech|b\.?e\.?|bachelor|m\.?tech|master|mca|bca|any graduate)", re.I)

def _extract_min_cgpa(text: str) -> float | None:
    if not text:
        return None
    m = re.search(r"(?:cgpa|gpa)\s*(?:of|:)?\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    return float(m.group(1)) if m else None

def evaluate(job: JobPosting, student: StudentProfile) -> EligibilityResult:
    reasons, blockers = [], []
    status = "eligible"
    
    # CGPA check
    required_cgpa = _extract_min_cgpa(job.education_requirements or "") or _extract_min_cgpa(job.description)
    if required_cgpa and student.cgpa is not None:
        if student.cgpa >= required_cgpa:
            reasons.append(f"✓ CGPA {student.cgpa:.2f} satisfies required criteria ({required_cgpa})")
        else:
            blockers.append(f"✗ CGPA {student.cgpa:.2f} is below mandatory threshold ({required_cgpa})")
            status = "not_eligible"
            
    # Backlogs check
    if "no backlog" in (job.education_requirements or "").lower() or "no active backlogs" in job.description.lower():
        if student.backlogs > 0:
            blockers.append(f"✗ Has {student.backlogs} active backlogs; posting mandates zero backlogs")
            status = "not_eligible"
            
    # Experience check
    if job.experience_min and job.experience_min > 0:
        student_exp = len(student.internships) * 0.25
        if student_exp >= job.experience_min:
            reasons.append(f"✓ Meets {job.experience_min}y experience via verified internships")
        elif job.experience_min <= 1:
            reasons.append(f"⚠ Minor experience gap: {job.experience_min}y required, student has ~{student_exp:.1f}y")
            if status == "eligible":
                status = "partially_eligible"
        else:
            blockers.append(f"✗ Requires {job.experience_min}y full-time experience")
            status = "not_eligible"
            
    if not reasons and not blockers:
        reasons.append("✓ Standard academic profile aligns with campus eligibility requirements")
        
    return EligibilityResult(status=status, reasons=reasons, blockers=blockers)

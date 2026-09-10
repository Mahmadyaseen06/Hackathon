"""
Curated Internship Opportunities & Hackathon Matcher
Matches student eligibility and tech stack against premier open-source,
research, and government internship programs.
"""

from __future__ import annotations
from typing import Dict, Any, List

INTERNSHIP_PROGRAMS: List[Dict[str, Any]] = [
    {
        "id": "gsoc_2026",
        "name": "Google Summer of Code (GSoC) 2026",
        "organization": "Google Open Source",
        "stipend": "Stipend ($1500 - $3000 USD based on country)",
        "timeline": "Applications Open: March 16, 2026 | Deadline: March 31, 2026",
        "eligibility": "Enrolled student or open-source contributor (18+)",
        "skills_needed": ["Git", "Python", "C++", "JavaScript", "Open Source"],
        "url": "https://summerofcode.withgoogle.com/",
        "description": "Prestigious global program pairing students with open source mentor organizations."
    },
    {
        "id": "isro_vssc_2026",
        "name": "ISRO VSSC Internship 2026",
        "organization": "Indian Space Research Organisation (ISRO)",
        "stipend": "Unpaid / Academic Credit + Certificate",
        "timeline": "Rolling cycles (Deadlines: October 31 & April 30)",
        "eligibility": "B.Tech/BE (CSE, ECE, Mech) with min 60% / 6.5 CGPA and 4th sem completed",
        "skills_needed": ["Python", "C++", "Signal Processing", "Machine Learning", "Embedded Systems"],
        "url": "https://www.vssc.gov.in/STUDENTS/",
        "description": "Work alongside space scientists on aerospace, remote sensing, and computing projects."
    },
    {
        "id": "sih_2026",
        "name": "Smart India Hackathon (SIH) 2026",
        "organization": "Ministry of Education & AICTE",
        "stipend": "₹1,00,000 Cash Prize per problem statement",
        "timeline": "College internal rounds: August | Grand Finale: Nov/Dec",
        "eligibility": "Team of 6 engineering students (at least 1 female teammate mandatory)",
        "skills_needed": ["Full-Stack", "Mobile App Dev", "AI/ML", "Cloud", "IoT"],
        "url": "https://www.sih.gov.in/",
        "description": "World's biggest open innovation hackathon solving real government and industry challenges."
    },
    {
        "id": "nptel_internship",
        "name": "NPTEL SWAYAM Online Internship",
        "organization": "IIT Madras / NPTEL",
        "stipend": "Financial support & project mentorship",
        "timeline": "Summer (May-July) & Winter (Dec-Jan) cycles",
        "eligibility": "Top 2-5% performers in NPTEL proctored course examinations",
        "skills_needed": ["Domain Specific based on NPTEL Course"],
        "url": "https://nptel.ac.in/",
        "description": "Exclusive internship opportunity under IIT professors for top NPTEL certification scorers."
    }
]

def match_internships(student_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Match student profile to programs with match percentages and justification."""
    skills = student_data.get("skills", {})
    student_skill_names = [s.lower() for s in skills.keys()]
    cgpa = float(student_data.get("cgpa", 7.0))
    
    matched = []
    for prog in INTERNSHIP_PROGRAMS:
        needed = prog["skills_needed"]
        skill_hits = sum(1 for req in needed if any(req.lower() in s for s in student_skill_names))
        match_score = int((skill_hits / max(len(needed), 1)) * 100)
        
        # Boost for strong CGPA
        if cgpa >= 7.5:
            match_score = min(100, match_score + 10)
            
        matched.append({
            **prog,
            "match_percentage": match_score,
            "status": "Recommended" if match_score >= 60 else "Eligible to Apply"
        })
        
    matched.sort(key=lambda x: x["match_percentage"], reverse=True)
    return matched

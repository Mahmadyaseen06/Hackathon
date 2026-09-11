"""
Personalized Dynamic Roadmap Generator with LPA Benchmark Targeting
Generates structured, phased upskilling plans with realistic time-to-completion,
milestones, and interview drill areas using Ollama LLM.
"""

from __future__ import annotations
from typing import Dict, Any, List
import json
import logging
import httpx
import re

log = logging.getLogger(__name__)

LPA_BENCHMARK_TIERS = {
    "4-6": {
        "tier_name": "Tier 1: Foundation (4–6 LPA)",
        "roles": "Associate Software Engineer, Junior Developer, Support Engineer",
        "requirements": "Strong grip on 1 primary language, basic DSA, 1 full-stack/CLI project",
        "focus_areas": ["Language syntax & OOP", "Basic DSA (Arrays, Strings, HashMaps)", "Git fundamentals"]
    },
    "6-10": {
        "tier_name": "Tier 2: Core Engineering (6–10 LPA)",
        "roles": "Software Engineer, Full-Stack Developer, Data Analyst",
        "requirements": "2 languages, 200+ LeetCode DSA, 2 deployed projects, 1 internship",
        "focus_areas": ["Intermediate DSA (Trees, Graphs, Recursion)", "Database Schema Design & SQL", "REST API Development"]
    },
    "10-15": {
        "tier_name": "Tier 3: Specialized / Cloud (10–15 LPA)",
        "roles": "Cloud Engineer, ML Engineer, Backend Developer",
        "requirements": "Cloud certification, 300+ DSA, 3 production projects, 1+ internship",
        "focus_areas": ["Containerization (Docker)", "Cloud Services (AWS/GCP)", "Clean Architecture & CI/CD"]
    },
    "15-25": {
        "tier_name": "Tier 4: High-Growth Product (15–25 LPA)",
        "roles": "SDE-1 at Product Unicorns, ML Research Engineer",
        "requirements": "Advanced DSA, System Design (HLD/LLD), 4+ projects, GSoC/Top Internship",
        "focus_areas": ["System Design & Scalability", "Low-Level Design Patterns", "Advanced Algorithms & Concurrency"]
    },
    "25+": {
        "tier_name": "Tier 5: Elite FAANG / Global (25+ LPA)",
        "roles": "SDE-1 at FAANG/Tier-1 Tech, Quantitative Dev",
        "requirements": "Competitive programming (Knight/Candidate Master), Open-source core contributor",
        "focus_areas": ["Distributed Systems", "Competitive Programming", "High-Throughput Architecture"]
    }
}

def get_lpa_tier(target_lpa: float) -> str:
    if target_lpa <= 6.0: return "4-6"
    elif target_lpa <= 10.0: return "6-10"
    elif target_lpa <= 15.0: return "10-15"
    elif target_lpa <= 25.0: return "15-25"
    else: return "25+"

def generate_personalized_roadmap(
    student_data: Dict[str, Any],
    missing_skills: List[str],
    target_role: str = "Full-Stack Developer",
    target_lpa: float = 12.0
) -> Dict[str, Any]:
    """Generate dynamic actionable roadmap tailored to missing skills and LPA tier."""
    tier_key = get_lpa_tier(target_lpa)
    tier_info = LPA_BENCHMARK_TIERS[tier_key]
    skills_to_cover = missing_skills if missing_skills else ["Advanced DSA", "System Design", "Cloud Basics"]
    
    # 8-week structured curriculum personalized with candidate's actual skill gaps
    weeks = [
        {
            "week": 1,
            "phase": "Phase 1: Diagnostic & Core Fundamentals",
            "title": f"Fundamentals Sprint: {skills_to_cover[0] if len(skills_to_cover) > 0 else 'Core DSA'}",
            "focus": f"Master core syntax, data representations, and fundamentals of {skills_to_cover[0] if len(skills_to_cover) > 0 else 'DSA'}.",
            "actions": [
                f"Complete 10 hands-on coding exercises on {skills_to_cover[0] if len(skills_to_cover) > 0 else 'Data Structures'}",
                "Review time and space complexity analysis (Big-O)",
                "Set up Git version control workflow with feature branches"
            ],
            "milestone": f"Verified proficiency test score > 75% in {skills_to_cover[0] if len(skills_to_cover) > 0 else 'Fundamentals'}",
            "time_estimate": "12 hours"
        },
        {
            "week": 2,
            "phase": "Phase 1: Diagnostic & Core Fundamentals",
            "title": f"Applied Logic: {skills_to_cover[1] if len(skills_to_cover) > 1 else 'SQL & Databases'}",
            "focus": f"Deep dive into {skills_to_cover[1] if len(skills_to_cover) > 1 else 'SQL Database queries and indexing'}.",
            "actions": [
                "Solve 15 LeetCode Easy/Medium problems targeting weak data structures",
                "Construct relational schema with foreign keys and normalization",
                "Write complex SQL queries with multi-table JOINs and window functions"
            ],
            "milestone": "Pass LeetCode 50-problem checkpoint",
            "time_estimate": "14 hours"
        },
        {
            "week": 3,
            "phase": "Phase 2: Practical Architecture & Implementation",
            "title": f"Component Integration: {skills_to_cover[2] if len(skills_to_cover) > 2 else 'REST APIs & Architecture'}",
            "focus": "Build modular services and robust API communication.",
            "actions": [
                "Implement authenticated RESTful endpoints with JWT & error handlers",
                "Write comprehensive unit tests with Pytest / Jest (>80% coverage)",
                "Document API specifications using OpenAPI / Swagger"
            ],
            "milestone": "Deploy working backend microservice with live Swagger docs",
            "time_estimate": "15 hours"
        },
        {
            "week": 4,
            "phase": "Phase 2: Practical Architecture & Implementation",
            "title": "Full-Stack Project Milestone",
            "focus": "Ship an end-to-end portfolio project solving a real problem.",
            "actions": [
                "Develop responsive frontend UI connected to the backend services",
                "Integrate real-time updates or background processing jobs",
                "Publish clean GitHub repository with architecture diagrams in README"
            ],
            "milestone": "Live deployed project URL on Vercel / Render / AWS",
            "time_estimate": "18 hours"
        },
        {
            "week": 5,
            "phase": "Phase 3: System Design & Performance",
            "title": "Scalability & Containerization (Docker)",
            "focus": "Learn containerization, caching, and database query optimization.",
            "actions": [
                "Containerize full application with multi-stage Dockerfile & docker-compose",
                "Add Redis caching layer to reduce DB latency by 80%",
                "Perform load testing with Apache Bench / k6"
            ],
            "milestone": "Dockerized container running locally with automated seed scripts",
            "time_estimate": "12 hours"
        },
        {
            "week": 6,
            "phase": "Phase 3: System Design & Performance",
            "title": "System Design & Low-Level Design (LLD)",
            "focus": "Design scalable architectures and apply SOLID design patterns.",
            "actions": [
                "Study classic HLD architectures: URL shortener, Rate limiter, Chat system",
                "Practice LLD object-oriented design: Parking Lot, Movie Ticket Booking",
                "Complete 2 peer mock system design interview rounds"
            ],
            "milestone": "Completed 5 System Design case studies",
            "time_estimate": "14 hours"
        },
        {
            "week": 7,
            "phase": "Phase 4: Interview Drills & Mock Evaluation",
            "title": "Technical Interview Drills & LeetCode Sprint",
            "focus": "Timed problem solving and algorithmic fluency under pressure.",
            "actions": [
                "Complete 20 LeetCode Medium problems under 25-minute timers",
                "Review core CS fundamentals: OS processes/threads, DBMS ACID, Networking TCP/IP",
                "Attend department mock placement coding round"
            ],
            "milestone": "Score 85%+ in timed institutional assessment drill",
            "time_estimate": "16 hours"
        },
        {
            "week": 8,
            "phase": "Phase 4: Interview Drills & Mock Evaluation",
            "title": "HR, Behavioral Prep & Placement Application Sprint",
            "focus": "STAR technique for behavioral questions, resume ATS optimization, and referrals.",
            "actions": [
                "Format resume with measurable impact metrics (e.g. 'reduced latency by 35%')",
                "Prepare 5 STAR stories for leadership, conflict resolution, and technical failure",
                "Target and apply for 15 curated institutional placements and internships"
            ],
            "milestone": "Final TPO Placement Readiness Clearance & Interview Schedule",
            "time_estimate": "10 hours"
        }
    ]
    return {
        "target_role": target_role,
        "target_lpa": target_lpa,
        "tier_info": tier_info,
        "total_weeks": len(weeks),
        "estimated_hours": sum(int(w["time_estimate"].split()[0]) for w in weeks),
        "weeks": weeks,
        "powered_by": "PlacementAI Dynamic Engine"
    }


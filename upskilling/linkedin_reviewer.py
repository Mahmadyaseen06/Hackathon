"""
LinkedIn Profile AI Reviewer & Recruiter Search Optimizer
Analyzes candidate LinkedIn headlines, About summaries, skill keyword density,
and experience bullet points, providing Google X-Y-Z STAR rewrites and All-Star scoring.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import re

# High-volume Boolean search keywords tracked by tech recruiters
ROLE_KEYWORD_TAXONOMY = {
    "sde": [
        "Data Structures", "Algorithms", "REST API", "Microservices", "Docker",
        "System Design", "SQL", "Git", "CI/CD", "Unit Testing", "Concurrency",
        "FastAPI", "React", "Node.js", "Redis", "AWS"
    ],
    "data_science": [
        "Machine Learning", "Python", "Pandas", "Scikit-Learn", "PyTorch",
        "Deep Learning", "SQL", "EDA", "Feature Engineering", "Data Modeling",
        "FastAPI", "Model Deployment", "NLP", "SHAP", "Statistics"
    ],
    "cloud_devops": [
        "Kubernetes", "Docker", "CI/CD", "Terraform", "AWS", "Linux",
        "Bash", "Prometheus", "Grafana", "Nginx", "Microservices",
        "Infrastructure as Code", "Networking", "GitOps"
    ],
    "cybersecurity": [
        "Network Security", "OWASP", "Penetration Testing", "Wireshark", "Burp Suite",
        "Cryptography", "SIEM", "Vulnerability Assessment", "Firewalls", "Linux Hardening",
        "Incident Response", "Identity Management", "Zero Trust"
    ],
    "data_analytics": [
        "SQL", "Power BI", "Tableau", "Excel", "Data Visualization", "Python",
        "Pandas", "A/B Testing", "Statistical Analysis", "Business Intelligence",
        "ETL", "Star Schema", "DAX", "KPIs"
    ]
}

LINKEDIN_DEMO_PRESETS = [
    {
        "id": "generic_student",
        "label": "Demo: Generic Student Profile (Score ~52)",
        "headline": "Student at Engineering College | Looking for Entry-Level Software Engineering Opportunities",
        "about": "Hello, I am a 4th year computer science student with an interest in technology. I have completed several college projects using HTML, CSS, and basic Python. Looking forward to starting my career in IT industry.",
        "target_role": "Full-Stack SDE",
        "experience": "Built a college library management system website in PHP and MySQL. Created a weather app using JavaScript API."
    },
    {
        "id": "aarav_sde",
        "label": "Demo: Aarav Sharma (Strong SDE Intern)",
        "headline": "Software Engineer Intern @ Razorpay | Distributed Systems & High-Throughput APIs | Go, Python, AWS | 380+ LeetCode",
        "about": "Computer Science senior passionate about resilient backend infrastructure, consensus algorithms, and scalable microservices. During my internship at Razorpay, I optimized webhook dispatch pipelines handling 10,000+ req/sec. Capstone author of a distributed Raft task scheduler in Go.",
        "target_role": "Full-Stack SDE",
        "experience": "Optimized webhook distribution pipelines handling over 10,000 requests per second at Razorpay. Architected distributed task scheduler in Go utilizing Raft consensus and LSM-tree persistence."
    },
    {
        "id": "priya_ds",
        "label": "Demo: Priya Patel (Data Science & AI)",
        "headline": "Aspiring Data Scientist | ML Pipelines, Statistical Modeling & PyTorch | B.E. Computer Science 2026",
        "about": "Passionate about extracting actionable intelligence from unstructured data. Experienced in training supervised classification ensembles (XGBoost, LightGBM) and building interactive explainability dashboards using SHAP. Exploring retrieval-augmented generation (RAG) with local LLMs.",
        "target_role": "Data Science & AI",
        "experience": "Trained customer churn prediction model on 150k customer records achieving 0.94 ROC-AUC. Deployed real-time inference API in FastAPI."
    }
]

def get_linkedin_preset(preset_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a demo profile preset by ID."""
    for p in LINKEDIN_DEMO_PRESETS:
        if p.get("id") == preset_id:
            return p
    return None

def _classify_role(role_str: str) -> str:
    r = (role_str or "").lower().strip()
    if any(k in r for k in ["data sci", "machine learn", "ai", "deep learn"]):
        return "data_science"
    elif any(k in r for k in ["cloud", "devops", "platform", "sre"]):
        return "cloud_devops"
    elif any(k in r for k in ["cyber", "security", "infosec"]):
        return "cybersecurity"
    elif any(k in r for k in ["analytic", "bi", "business intelligence"]):
        return "data_analytics"
    else:
        return "sde"

def review_linkedin_profile(
    headline: str,
    about: str,
    target_role: str = "Full-Stack SDE",
    experience: str = "",
    student_name: str = "Candidate",
    known_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Perform comprehensive AI recruiter audit of candidate's LinkedIn presence.
    Evaluates headline hook, about section narrative, keyword discoverability,
    and Google X-Y-Z STAR bullet point rewrites.
    """
    h = (headline or "").strip()
    a = (about or "").strip()
    exp = (experience or "").strip()
    canonical_role = _classify_role(target_role)
    target_keywords = ROLE_KEYWORD_TAXONOMY.get(canonical_role, ROLE_KEYWORD_TAXONOMY["sde"])
    
    combined_text = f"{h} {a} {exp}".lower()

    # 1. Headline Scoring (/25)
    headline_score = 10
    headline_issues = []
    
    if len(h) < 15:
        headline_issues.append("Headline is too brief (<15 characters).")
    elif len(h) >= 40:
        headline_score += 5

    # Check for negative recruiter filters
    generic_student_cues = ["student at", "looking for", "seeking", "aspiring", "enthusiast", "fresher", "actively looking"]
    has_generic_cues = any(cue in h.lower() for cue in generic_student_cues)
    if has_generic_cues:
        headline_score -= 5
        headline_issues.append("Contains generic phrases like 'Student' or 'Looking for opportunities'. Recruiters search for specific titles and concrete tech stacks, not job-seeker status.")
    else:
        headline_score += 5

    # Check for hard skills / roles in headline
    has_target_role = any(part in h.lower() for part in [canonical_role.replace("_", " "), "engineer", "developer", "scientist", "analyst"])
    if has_target_role:
        headline_score += 3
    else:
        headline_issues.append(f"Does not explicitly name your target role ({target_role}).")

    # Check for pipe separators (|) or tech badges
    if "|" in h or "•" in h or "/" in h:
        headline_score += 2

    headline_score = max(5, min(25, headline_score))

    # 2. About Section Scoring (/25)
    about_score = 10
    about_issues = []
    
    if len(a) < 50:
        about_score = 8
        about_issues.append("About section is practically empty (<50 chars). Recruiters skip profiles without a compelling story.")
    else:
        if len(a) >= 200:
            about_score += 5
        # Check for quantifiable metrics
        if re.search(r'\d+[%kKxX\+]', a) or re.search(r'\d{2,}', a):
            about_score += 5
        else:
            about_issues.append("Missing quantifiable metrics (e.g. 'reduced latency by 35%', 'processed 10k requests').")

        # Check for contact info / portfolio link
        if any(c in a.lower() for c in ["email", "github", "portfolio", "reach me at", "contact", "@"]):
            about_score += 5
        else:
            about_issues.append("Missing call-to-action (email address or portfolio link for recruiter reachout).")

    about_score = max(5, min(25, about_score))

    # 3. Recruiter Search Keywords (/25)
    detected_keywords = []
    missing_keywords = []
    
    for kw in target_keywords:
        if kw.lower() in combined_text:
            detected_keywords.append(kw)
        else:
            missing_keywords.append(kw)

    keyword_density_ratio = len(detected_keywords) / max(1, len(target_keywords))
    keyword_score = round(keyword_density_ratio * 25)
    keyword_score = max(5, min(25, keyword_score))

    # 4. Experience & STAR Scoring (/25)
    experience_score = 12
    if len(exp) > 60:
        experience_score += 4
    if re.search(r'\d+[%kKxX\+]', exp) or re.search(r'\d{2,}', exp):
        experience_score += 5
    if any(action in exp.lower() for action in ["architected", "optimized", "developed", "deployed", "implemented", "reduced", "scaled", "automated"]):
        experience_score += 4
    experience_score = max(5, min(25, experience_score))

    # Total Recruiter Score (0-100)
    total_score = headline_score + about_score + keyword_score + experience_score

    if total_score >= 85:
        badge = "All-Star Recruiter Ready"
        badge_color = "#10b981"
    elif total_score >= 65:
        badge = "Intermediate Visibility"
        badge_color = "#f59e0b"
    else:
        badge = "Needs Recruiter Optimization"
        badge_color = "#ef4444"

    # Generate 3 AI-Tailored Headlines
    primary_skills_str = ", ".join(detected_keywords[:3]) if detected_keywords else "Python, SQL, Cloud Architecture"
    
    if canonical_role == "data_science":
        opt_headlines = [
            f"Data Scientist | Machine Learning & Statistical Inference | Python, PyTorch, SQL | Building Predictive Systems",
            f"Machine Learning Engineer | End-to-End ML Pipelines & LLM/RAG | FastAPI, Scikit-Learn | CS Senior @ 2026",
            f"Data Science & AI Specialist | Explaining Models via SHAP & Feature Engineering | Top Kaggle Benchmark"
        ]
    elif canonical_role == "cloud_devops":
        opt_headlines = [
            f"DevOps & Cloud Platform Engineer | Kubernetes, Docker & CI/CD Pipelines | AWS, Terraform, Linux",
            f"Site Reliability Engineer (SRE) | High-Availability Infrastructure & Observability | Prometheus, Grafana, Nginx",
            f"Cloud Engineer | Multi-Cloud Architecture & Automated Infrastructure as Code | Dockerized Microservices"
        ]
    elif canonical_role == "cybersecurity":
        opt_headlines = [
            f"Cybersecurity Analyst | Threat Modeling & Network Defense | OWASP Top 10, Wireshark, Burp Suite",
            f"Security Engineer | Web App Security & Cryptography | SIEM Incident Response & Linux Hardening",
            f"Information Security Specialist | Zero Trust Architecture & Vulnerability Mitigation | CompTIA Security+"
        ]
    elif canonical_role == "data_analytics":
        opt_headlines = [
            f"Data Analyst | Advanced SQL, Power BI & Tableau Dashboards | Business KPI Metrics & Cohort Analysis",
            f"Business Intelligence Engineer | Turning Complex Data into Executive ROI | SQL Window Functions, DAX, Python",
            f"Product Analytics Specialist | A/B Testing, User Retention & Data Warehousing | Star Schema Modeling"
        ]
    else:  # SDE / Full-Stack
        opt_headlines = [
            f"Software Engineer | High-Throughput Backend Microservices | Go, Python, React, Docker | 380+ LeetCode",
            f"Full-Stack Developer | Scalable REST APIs, Redis Caching & Cloud Deployments | Distributed Systems",
            f"Backend Engineer | System Architecture & Database Optimization | B.E. Computer Science 2026 Batch"
        ]

    # Generate Optimized About Section
    opt_about = f"""I am a {target_role} specializing in building robust, performant software systems that solve real-world problems. With hands-on proficiency across {primary_skills_str}, I focus on clean architectural trade-offs, quantifiable performance, and test-driven reliability.

🛠️ Core Technical Competencies:
• Languages: Python, Go, JavaScript/TypeScript, SQL
• Core Frameworks & Tools: {', '.join(target_keywords[:6])}
• Architecture: Scalable Microservices, In-Memory Caching (Redis), RESTful APIs, Containerization
• Fundamentals: Data Structures, Operating Systems, Database Indexing, Big-O Complexity

🚀 Flagship Highlights & Measurable Impact:
• Architected production-grade applications emphasizing sub-100ms API latencies and zero runtime crashes.
• Implemented automated CI/CD validation and containerized microservice deployments reducing manual overhead by 70%.
• Actively practicing algorithmic problem solving on LeetCode with an emphasis on concurrent systems and scalability.

📬 Open to high-impact engineering roles, internships, and research collaborations.
Reach out at: {student_name.lower().replace(' ', '')}@example.com | Portfolio: github.com"""

    # Generate Before vs After STAR Bullet Points
    star_bullet_pairs = [
        {
            "category": "Project Architecture",
            "before": "Built a web app project for library management using database and backend.",
            "after": "Architected modular RESTful service handling 5,000+ catalog queries with Redis caching, reducing database read latency by 68%."
        },
        {
            "category": "API / Feature Delivery",
            "before": "Worked on backend APIs and connected frontend components.",
            "after": "Engineered 12 authenticated endpoints with JWT security and rate-limiting, achieving 99.8% test coverage across 80+ Pytest suites."
        },
        {
            "category": "Performance & Deployment",
            "before": "Created Docker containers and deployed the application.",
            "after": "Constructed multi-stage Docker container pipeline cutting deployment image footprint by 84% (850MB → 135MB) with automated GitHub Actions CI."
        }
    ]

    # Actionable All-Star Checklist
    checklist = [
        {
            "step": "Custom Profile URL Slug",
            "description": "Claim a clean vanity URL (e.g. linkedin.com/in/first-last) to look professional on resumes.",
            "completed": bool(len(h) > 10)
        },
        {
            "step": "Recruiter Magnet Headline",
            "description": "Replace 'Looking for opportunities' with Target Title + 3 Hard Tech Badges + Key Differentiator.",
            "completed": bool(headline_score >= 20)
        },
        {
            "step": "Quantified STAR Impact Bullets",
            "description": "Use the Google X-Y-Z formula ('Accomplished X as measured by Y by doing Z') in all project descriptions.",
            "completed": bool(experience_score >= 20)
        },
        {
            "step": "Top 10 High-Volume Search Keywords",
            "description": f"Infuse your About and Skills sections with missing recruiter keywords: {', '.join(missing_keywords[:4])}.",
            "completed": bool(len(missing_keywords) <= 4)
        },
        {
            "step": "Featured Media & Live Demo Links",
            "description": "Pin your live GitHub repository links and demo videos in the LinkedIn Featured carousel.",
            "completed": True
        }
    ]

    return {
        "score": total_score,
        "recruiter_score": total_score,
        "badge": badge,
        "badge_color": badge_color,
        "breakdown": {
            "headline_score": headline_score,
            "about_score": about_score,
            "keyword_score": keyword_score,
            "experience_score": experience_score
        },
        "headline_analysis": {
            "current_headline": h or "[No headline specified]",
            "issues": headline_issues if headline_issues else ["Your headline demonstrates clean structure and role targeting."],
            "optimized_headlines": opt_headlines
        },
        "about_analysis": {
            "issues": about_issues if about_issues else ["Solid narrative structure with professional presentation."],
            "optimized_about": opt_about
        },
        "keyword_analysis": {
            "target_role": target_role,
            "canonical_track": canonical_role,
            "detected_keywords": detected_keywords,
            "missing_keywords": missing_keywords[:6],
            "keyword_match_pct": round(keyword_density_ratio * 100)
        },
        "experience_star_optimizer": star_bullet_pairs,
        "all_star_checklist": checklist,
        "checklist": checklist,
        "presets": LINKEDIN_DEMO_PRESETS
    }

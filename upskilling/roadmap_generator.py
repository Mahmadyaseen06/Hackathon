"""
Personalized Dynamic Roadmap Generator with Multi-Course Domain Targeting
Generates structured, phased 8-week upskilling plans tailored by career track
(Full-Stack SDE, Data Science & AI, Cloud & DevOps, Cybersecurity, Data Analytics),
incorporating student's specific missing skills and target LPA benchmarks.
"""

from __future__ import annotations
from typing import Dict, Any, List
import logging
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

AVAILABLE_TRACKS = [
    {
        "id": "sde",
        "title": "Full-Stack SDE",
        "icon": "🚀",
        "description": "DSA, Web Microservices, Distributed Systems & LeetCode Sprints"
    },
    {
        "id": "data_science",
        "title": "Data Science & AI",
        "icon": "🤖",
        "description": "Python, Pandas, Scikit-Learn, PyTorch, RAG & Production ML Deployment"
    },
    {
        "id": "cloud_devops",
        "title": "Cloud & DevOps",
        "icon": "☁️",
        "description": "Linux, Docker, Kubernetes, CI/CD, Terraform & AWS/GCP Architecture"
    },
    {
        "id": "cybersecurity",
        "title": "Cybersecurity",
        "icon": "🛡️",
        "description": "Network Protocols, OWASP Top 10, Cryptography & SIEM Incident Defense"
    },
    {
        "id": "data_analytics",
        "title": "Data Analytics",
        "icon": "📊",
        "description": "Advanced SQL, Power BI/Tableau, Statistical A/B Testing & Data Warehousing"
    }
]

def get_lpa_tier(target_lpa: float) -> str:
    if target_lpa <= 6.0: return "4-6"
    elif target_lpa <= 10.0: return "6-10"
    elif target_lpa <= 15.0: return "10-15"
    elif target_lpa <= 25.0: return "15-25"
    else: return "25+"

def _match_track(role_or_track: str) -> str:
    """Normalize input role or track string to one of 5 supported canonical tracks."""
    r = (role_or_track or "").lower().strip()
    if any(k in r for k in ["data sci", "machine learn", "ai ", "ai/", "deep learn", "nlp", "llm", "ml engineer"]):
        return "data_science"
    elif any(k in r for k in ["cloud", "devops", "sre", "platform", "infrastructure", "site reliability"]):
        return "cloud_devops"
    elif any(k in r for k in ["cyber", "security", "infosec", "soc", "penetration", "threat"]):
        return "cybersecurity"
    elif any(k in r for k in ["analytic", "business intell", "bi dev", "bi engineer", "data analyst"]):
        return "data_analytics"
    else:
        return "sde"

def _build_sde_curriculum(skills: List[str]) -> List[Dict[str, Any]]:
    s0 = skills[0] if len(skills) > 0 else "Data Structures & Algorithms"
    s1 = skills[1] if len(skills) > 1 else "Database Schema Design & SQL"
    s2 = skills[2] if len(skills) > 2 else "REST APIs & Backend Architecture"
    return [
        {
            "week": 1,
            "phase": "Phase 1: Diagnostic & Core Fundamentals",
            "title": f"Algorithmic Foundations: {s0}",
            "focus": f"Master core syntax, Big-O complexity, and foundational problem patterns in {s0}.",
            "actions": [
                f"Complete 12 hands-on coding exercises focused on {s0}",
                "Analyze time and space complexity trade-offs for array, hashmap, and two-pointer paradigms",
                "Set up professional Git branching workflow with semantic commit messages"
            ],
            "milestone": f"Achieve >80% accuracy on timed {s0} assessment drill",
            "time_estimate": "12 hours"
        },
        {
            "week": 2,
            "phase": "Phase 1: Diagnostic & Core Fundamentals",
            "title": f"Applied Logic & Data Persistence: {s1}",
            "focus": f"Deep dive into relational database normalization, indexing, and query optimization.",
            "actions": [
                "Construct 3NF relational schemas with primary/foreign keys and compound indexes",
                "Write complex analytical SQL queries using window functions, multi-table JOINs, and CTEs",
                "Solve 15 LeetCode Easy/Medium algorithmic problems targeting weak concepts"
            ],
            "milestone": "Pass LeetCode 50-problem checkpoint with 0 syntax warnings",
            "time_estimate": "14 hours"
        },
        {
            "week": 3,
            "phase": "Phase 2: Microservices & Implementation",
            "title": f"Component Integration: {s2}",
            "focus": "Build modular services, authenticated RESTful endpoints, and robust error middleware.",
            "actions": [
                "Implement authenticated RESTful APIs with JWT security, rate-limiting, and validation schemas",
                "Write comprehensive unit and integration tests with Pytest / Jest (>85% code coverage)",
                "Publish interactive OpenAPI / Swagger specifications for client consumption"
            ],
            "milestone": "Deploy working backend microservice with live OpenAPI documentation",
            "time_estimate": "15 hours"
        },
        {
            "week": 4,
            "phase": "Phase 2: Microservices & Implementation",
            "title": "Full-Stack Portfolio Project Milestone",
            "focus": "Ship an end-to-end production application solving a real-world high-throughput problem.",
            "actions": [
                "Develop responsive frontend UI connected seamlessly to the backend service endpoints",
                "Integrate asynchronous background task queuing or WebSocket event streams",
                "Publish clean GitHub repository featuring system architecture diagrams in README"
            ],
            "milestone": "Live deployed project URL on Render / Vercel / AWS with zero downtime",
            "time_estimate": "18 hours"
        },
        {
            "week": 5,
            "phase": "Phase 3: System Design & Performance",
            "title": "Scalability, Caching & Containerization (Docker)",
            "focus": "Learn containerization, in-memory caching strategies, and database latency reduction.",
            "actions": [
                "Containerize multi-tier services using multi-stage Dockerfiles and docker-compose",
                "Implement Redis caching layer to reduce database read latencies by over 75%",
                "Execute stress testing with k6 or Apache Bench simulating 500 concurrent connections"
            ],
            "milestone": "Dockerized container bundle running locally with automated seed scripts",
            "time_estimate": "14 hours"
        },
        {
            "week": 6,
            "phase": "Phase 3: System Design & Performance",
            "title": "System Design (HLD) & Low-Level Design (LLD)",
            "focus": "Architect scalable systems, handle failover mechanisms, and apply SOLID design patterns.",
            "actions": [
                "Study classic HLD architectures: URL Shortener, Rate Limiter, and Notification Pipeline",
                "Practice LLD object-oriented designs: Parking Lot, Movie Ticket Booking, and Ride Hailing",
                "Participate in 2 peer system design mock interviews focusing on trade-offs and CAP theorem"
            ],
            "milestone": "Complete 5 end-to-end System Design architecture blueprints with tradeoff justifications",
            "time_estimate": "14 hours"
        },
        {
            "week": 7,
            "phase": "Phase 4: Interview Drills & Mock Evaluation",
            "title": "Technical Interview Drills & LeetCode Sprint",
            "focus": "High-pressure timed problem solving, tree/graph traversal, and live coding communication.",
            "actions": [
                "Complete 20 LeetCode Medium problems under strict 25-minute timers",
                "Review core CS fundamentals: Operating Systems (Threads/Processes), Networks, DBMS ACID",
                "Conduct live voice mock interviews on the AI Mock Interview platform"
            ],
            "milestone": "Score 85%+ in timed institutional assessment coding sprint",
            "time_estimate": "16 hours"
        },
        {
            "week": 8,
            "phase": "Phase 4: Interview Drills & Mock Evaluation",
            "title": "STAR Behavioral, Resume ATS & Placement Sprint",
            "focus": "STAR technique for leadership and technical failure questions, ATS resume polish, and referrals.",
            "actions": [
                "Format resume with measurable impact metrics (e.g. 'reduced latency by 35% across 10k req/s')",
                "Prepare 5 structured STAR narratives for teamwork, strict deadlines, and production outages",
                "Target and apply for 15 curated institutional placements and top tech recruitment drives"
            ],
            "milestone": "Final TPO Placement Readiness Clearance & Confirmed Interview Slots",
            "time_estimate": "10 hours"
        }
    ]

def _build_data_science_curriculum(skills: List[str]) -> List[Dict[str, Any]]:
    s0 = skills[0] if len(skills) > 0 else "Pandas & Data Wrangling"
    s1 = skills[1] if len(skills) > 1 else "Feature Engineering & Scikit-Learn"
    s2 = skills[2] if len(skills) > 2 else "PyTorch & Deep Learning"
    return [
        {
            "week": 1,
            "phase": "Phase 1: Mathematical Foundations & Data Ingestion",
            "title": f"Vectorized Computing & Data Cleaning: {s0}",
            "focus": "Master vectorized arrays, dataframe manipulations, handling missing values, and outlier detection.",
            "actions": [
                "Perform complex slicing, grouping, and aggregations across 500k+ row datasets in Pandas",
                "Implement robust handling for imbalanced data, null imputations, and categorical encodings",
                "Calculate matrix operations, dot products, and vector spaces using NumPy"
            ],
            "milestone": "Publish automated Exploratory Data Analysis (EDA) notebook with statistical visualizations",
            "time_estimate": "12 hours"
        },
        {
            "week": 2,
            "phase": "Phase 1: Mathematical Foundations & Data Ingestion",
            "title": "Statistical Inference & Analytical SQL",
            "focus": "Hypothesis testing, distributions, probability theory, and complex analytical SQL queries.",
            "actions": [
                "Run parametric and non-parametric hypothesis tests (t-tests, Chi-square, ANOVA)",
                "Write complex SQL window functions, cohort aggregations, and rolling metrics",
                "Build correlation heatmaps and test for multicollinearity (VIF scores)"
            ],
            "milestone": "Deliver complete A/B test analysis notebook with p-values and confidence intervals",
            "time_estimate": "14 hours"
        },
        {
            "week": 3,
            "phase": "Phase 2: Supervised Learning & Feature Pipelines",
            "title": f"Supervised ML & Feature Pipelines: {s1}",
            "focus": "Train, tune, and evaluate classical machine learning models for regression and classification.",
            "actions": [
                "Train Random Forests, XGBoost, and LightGBM models with k-fold cross-validation",
                "Build automated scikit-learn Pipelines with column transformers and custom encoders",
                "Evaluate models using ROC-AUC, Precision-Recall curves, F1-score, and Confusion Matrices"
            ],
            "milestone": "Achieve top-quartile benchmark score on Kaggle / real-world dataset",
            "time_estimate": "15 hours"
        },
        {
            "week": 4,
            "phase": "Phase 2: Supervised Learning & Feature Pipelines",
            "title": "Unsupervised Learning, Clustering & SHAP Explainability",
            "focus": "Dimensionality reduction, clustering algorithms, and model interpretability with SHAP.",
            "actions": [
                "Apply PCA, t-SNE, and K-Means / DBSCAN for customer segmentation",
                "Compute SHAP TreeExplainer values and force plots to explain feature importances",
                "Package models into serialized artifacts (.joblib / .onnx) with metadata"
            ],
            "milestone": "Interactive Streamlit app explaining model predictions with live SHAP waterfall plots",
            "time_estimate": "16 hours"
        },
        {
            "week": 5,
            "phase": "Phase 3: Deep Learning & Generative AI",
            "title": f"Deep Learning Foundations: {s2}",
            "focus": "Neural network architectures, backpropagation, and PyTorch tensor computing.",
            "actions": [
                "Build and train custom Multi-Layer Perceptrons (MLP) and CNNs in PyTorch",
                "Implement learning rate schedulers, AdamW optimizers, and dropout regularization",
                "Monitor gradient descent and loss curves using TensorBoard or Weights & Biases"
            ],
            "milestone": "Trained PyTorch classifier achieving >90% test accuracy on unseen test split",
            "time_estimate": "16 hours"
        },
        {
            "week": 6,
            "phase": "Phase 3: Deep Learning & Generative AI",
            "title": "NLP, Embeddings & RAG Vector Search",
            "focus": "Tokenization, text embeddings, vector databases (Chroma/FAISS), and Retrieval-Augmented Generation.",
            "actions": [
                "Generate dense sentence embeddings using Hugging Face transformer models",
                "Index documents into a vector database with cosine similarity search",
                "Construct end-to-end RAG pipeline querying local LLM (Ollama) with citation context"
            ],
            "milestone": "Working RAG search tool capable of answering domain questions from PDF documents",
            "time_estimate": "15 hours"
        },
        {
            "week": 7,
            "phase": "Phase 4: MLOps, System Deployment & Drills",
            "title": "MLOps, Model Serving & FastAPI Deployment",
            "focus": "Containerized model APIs, inference latency optimization, and data drift monitoring.",
            "actions": [
                "Wrap trained ML/AI model in a high-speed asynchronous FastAPI endpoint",
                "Containerize model serving stack using Docker with health-check routes",
                "Set up input validation with Pydantic and batch inference endpoints"
            ],
            "milestone": "Live deployed ML prediction API with sub-100ms response time on Render / AWS",
            "time_estimate": "14 hours"
        },
        {
            "week": 8,
            "phase": "Phase 4: MLOps, System Deployment & Drills",
            "title": "Data Science Defense & Industry Placement Sprint",
            "focus": "Defending ML modeling decisions, metric trade-offs (precision vs recall), and portfolio showcase.",
            "actions": [
                "Prepare oral defense for capstone data projects: assumptions, data leaks, and failure modes",
                "Audit GitHub repository with reproducible requirements.txt and clean documentation",
                "Apply to 15 curated Data Scientist, ML Engineer, and AI Specialist campus hiring drives"
            ],
            "milestone": "Passed Data Science Technical Defense Mock & Final Placement Clearance",
            "time_estimate": "10 hours"
        }
    ]

def _build_cloud_devops_curriculum(skills: List[str]) -> List[Dict[str, Any]]:
    s0 = skills[0] if len(skills) > 0 else "Linux Internals & Shell Scripting"
    s1 = skills[1] if len(skills) > 1 else "Docker & Containerization"
    s2 = skills[2] if len(skills) > 2 else "Kubernetes & Orchestration"
    return [
        {
            "week": 1,
            "phase": "Phase 1: Operating Systems & Networking",
            "title": f"Linux Systems & Shell Automation: {s0}",
            "focus": "POSIX processes, systemd services, permissions, cron jobs, and advanced Bash scripting.",
            "actions": [
                "Write modular Bash automation scripts with error traps and logging",
                "Inspect system processes, memory maps, and file descriptors with htop, lsof, and strace",
                "Configure automated SSH key-based authentication with hardened sshd configs"
            ],
            "milestone": "Complete automated server provisioning and health-audit Bash script",
            "time_estimate": "12 hours"
        },
        {
            "week": 2,
            "phase": "Phase 1: Operating Systems & Networking",
            "title": "Networking Fundamentals, DNS & Reverse Proxies",
            "focus": "TCP/IP 4-layer model, HTTP/2, TLS/SSL termination, and Nginx reverse proxy configuration.",
            "actions": [
                "Configure Nginx reverse proxy with SSL certificates (Let's Encrypt / self-signed)",
                "Analyze network packets and handshake latencies using tcpdump and curl -w timings",
                "Implement rate limiting, gzip compression, and secure HTTP response headers"
            ],
            "milestone": "Fully functioning Nginx reverse proxy routing traffic across two backend services",
            "time_estimate": "14 hours"
        },
        {
            "week": 3,
            "phase": "Phase 2: Containerization & CI/CD Pipelines",
            "title": f"Microservice Containerization: {s1}",
            "focus": "Multi-stage Docker builds, image size minimization, and security vulnerabilities.",
            "actions": [
                "Construct multi-stage Dockerfiles reducing image footprint from 800MB to <90MB",
                "Manage multi-container networks with docker-compose (app, Redis, PostgreSQL)",
                "Run Trivy / Grype vulnerability scans against container images to remediate CVEs"
            ],
            "milestone": "Dockerized microservice stack passing zero-high-CVE security audit",
            "time_estimate": "14 hours"
        },
        {
            "week": 4,
            "phase": "Phase 2: Containerization & CI/CD Pipelines",
            "title": "Automated CI/CD Workflows (GitHub Actions)",
            "focus": "Continuous integration, automated test runners, artifact caching, and image publishing.",
            "actions": [
                "Build multi-stage GitHub Actions workflow executing linting, unit tests, and security scans",
                "Automate Docker image building and pushing to GitHub Packages (GHCR) or Docker Hub",
                "Implement semantic release tagging and automated deployment triggers on main branch push"
            ],
            "milestone": "100% automated CI/CD pipeline triggering automated test & build on every pull request",
            "time_estimate": "15 hours"
        },
        {
            "week": 5,
            "phase": "Phase 3: Kubernetes & Cloud Infrastructure",
            "title": f"Cluster Orchestration: {s2}",
            "focus": "Kubernetes Pods, Deployments, Services, Ingress, and ConfigMaps/Secrets.",
            "actions": [
                "Set up local Kubernetes cluster using Minikube or k3s",
                "Write declarative YAML manifests for Deployments, ClusterIP Services, and Ingress rules",
                "Implement RollingUpdate deployment strategies and Liveness/Readiness probe configurations"
            ],
            "milestone": "Deploy scalable 3-replica application in Kubernetes with zero-downtime rolling update",
            "time_estimate": "16 hours"
        },
        {
            "week": 6,
            "phase": "Phase 3: Kubernetes & Cloud Infrastructure",
            "title": "Infrastructure as Code (Terraform) & AWS/GCP Core",
            "focus": "Cloud provider core services (VPC, Subnets, IAM, EC2, S3) provisioned via Terraform.",
            "actions": [
                "Write modular Terraform code with state locking via remote S3 backend",
                "Provision isolated VPC with public/private subnets, Internet Gateway, and NAT Gateway",
                "Configure least-privilege IAM policies, roles, and security groups"
            ],
            "milestone": "Reproducible Terraform blueprint spinning up full cloud network in 1 command",
            "time_estimate": "16 hours"
        },
        {
            "week": 7,
            "phase": "Phase 4: Observability, SRE & Placement Sprint",
            "title": "Observability & SRE (Prometheus, Grafana & Logs)",
            "focus": "Monitoring metrics, alerting rules, centralized logging, and Incident Response.",
            "actions": [
                "Expose application metrics (/metrics) and scrape them into Prometheus",
                "Build Grafana dashboard tracking CPU, memory, request latency (p95/p99), and error rates",
                "Configure alerting rules for high error rates (HTTP 5xx > 2%)"
            ],
            "milestone": "Live Grafana dashboard providing real-time telemetry across cluster containers",
            "time_estimate": "14 hours"
        },
        {
            "week": 8,
            "phase": "Phase 4: Observability, SRE & Placement Sprint",
            "title": "DevOps Technical Defense & Campus Hiring Sprint",
            "focus": "Defending cloud architecture, failure recovery scenarios, and technical interviews.",
            "actions": [
                "Prepare oral defense for failover strategies: split-brain, database replication lag, and DDOS mitigation",
                "Complete AWS Cloud Practitioner / Solutions Architect Associate practice questions",
                "Target and apply for 15 curated Cloud Engineer, SRE, and DevOps recruitment drives"
            ],
            "milestone": "Cleared DevOps Systems Defense Mock & Final Placement Readiness Signoff",
            "time_estimate": "10 hours"
        }
    ]

def _build_cybersecurity_curriculum(skills: List[str]) -> List[Dict[str, Any]]:
    s0 = skills[0] if len(skills) > 0 else "Network Security & Packet Inspection"
    s1 = skills[1] if len(skills) > 1 else "OWASP Web Vulnerabilities"
    s2 = skills[2] if len(skills) > 2 else "Cryptography & Threat Modeling"
    return [
        {
            "week": 1,
            "phase": "Phase 1: Network Defense & Protocols",
            "title": f"Network Security & Packet Analysis: {s0}",
            "focus": "OSI 7-layer model, packet inspection with Wireshark, TCP handshakes, and port scanning.",
            "actions": [
                "Capture and analyze live network traffic using Wireshark and tcpdump to detect cleartext credentials",
                "Perform network reconnaissance and firewall mapping using Nmap syntax (-sS, -sV, -Pn)",
                "Identify ARP spoofing, DNS cache poisoning, and SYN flood attack signatures"
            ],
            "milestone": "Deliver comprehensive Network Threat Packet Capture (PCAP) forensic report",
            "time_estimate": "12 hours"
        },
        {
            "week": 2,
            "phase": "Phase 1: Network Defense & Protocols",
            "title": "Linux & Windows Host Hardening",
            "focus": "Operating system security baselines, permissions, auditd logging, and SSH defense.",
            "actions": [
                "Apply CIS Benchmark hardening guidelines to Ubuntu/Debian server installation",
                "Configure UFW / iptables firewall rules blocking unauthorized inbound ports",
                "Set up Linux auditd to monitor suspicious privilege escalation (sudoers edits)"
            ],
            "milestone": "Automated server hardening script scoring >85 on Lynis security auditor",
            "time_estimate": "14 hours"
        },
        {
            "week": 3,
            "phase": "Phase 2: Web Application Security & Pen Testing",
            "title": f"Web Application Security: {s1}",
            "focus": "OWASP Top 10 vulnerabilities: SQL Injection, XSS, CSRF, SSRF, and Broken Access Control.",
            "actions": [
                "Intercept and modify HTTP requests using Burp Suite Community Edition",
                "Exploit and remediate Blind/Time-based SQL injection vulnerabilities in sandbox environment",
                "Implement Content Security Policy (CSP) and parameterized queries to eliminate XSS/SQLi"
            ],
            "milestone": "Complete 10 PortSwigger Web Security Academy labs with documented PoCs",
            "time_estimate": "16 hours"
        },
        {
            "week": 4,
            "phase": "Phase 2: Web Application Security & Pen Testing",
            "title": "Authentication, API Security & JWT Exploits",
            "focus": "OAuth2 flows, JWT token tampering, IDOR vulnerabilities, and API rate limiting.",
            "actions": [
                "Audit REST APIs for Insecure Direct Object References (IDOR) and broken object-level authorization",
                "Demonstrate algorithm none attack and key confusion attacks on weak JWT implementations",
                "Implement secure session token rotation and PKCE flows for web clients"
            ],
            "milestone": "Full API security audit report with remediation pull request in code repository",
            "time_estimate": "15 hours"
        },
        {
            "week": 5,
            "phase": "Phase 3: Cryptography & Identity Defense",
            "title": f"Applied Cryptography & PKI: {s2}",
            "focus": "Symmetric/Asymmetric encryption (AES-256, RSA), SHA-256 hashing, and digital certificates.",
            "actions": [
                "Generate custom Certificate Authority (CA), intermediate certificates, and TLS keys with OpenSSL",
                "Explain differences between password hashing algorithms (bcrypt, Argon2 vs MD5/SHA)",
                "Implement end-to-end payload signing and verification using HMAC and public key cryptography"
            ],
            "milestone": "Working secure communication service with mutual TLS (mTLS) authentication",
            "time_estimate": "14 hours"
        },
        {
            "week": 6,
            "phase": "Phase 3: Cryptography & Identity Defense",
            "title": "Security Information & Event Management (SIEM)",
            "focus": "Log ingestion, correlation rules, incident triage, and MITRE ATT&CK framework.",
            "actions": [
                "Ingest syslog, web access logs, and auth logs into Elastic SIEM or Splunk Free",
                "Write detection rules for brute-force login attempts and lateral movement",
                "Map simulated attacks against MITRE ATT&CK tactics and techniques"
            ],
            "milestone": "Live SIEM dashboard with automated alert triggers on suspicious authentication anomalies",
            "time_estimate": "15 hours"
        },
        {
            "week": 7,
            "phase": "Phase 4: Threat Modeling & Interview Sprint",
            "title": "Threat Modeling & Incident Response Drills",
            "focus": "STRIDE threat modeling, root-cause postmortems, and cybersecurity interview case studies.",
            "actions": [
                "Perform STRIDE threat modeling against a cloud banking / e-commerce architecture",
                "Draft an incident response containment and eradication playbook for ransomware/data breach",
                "Complete 5 mock cybersecurity scenario interviews (Defense-in-depth, Zero Trust principles)"
            ],
            "milestone": "Completed STRIDE Threat Model document with Data Flow Diagrams (DFD)",
            "time_estimate": "14 hours"
        },
        {
            "week": 8,
            "phase": "Phase 4: Threat Modeling & Interview Sprint",
            "title": "Security Clearance & SOC Analyst Hiring Sprint",
            "focus": "Technical defense, security certifications (CompTIA Security+ / CEH), and job applications.",
            "actions": [
                "Format security portfolio highlighting bug bounties, lab writeups, and code remediation commits",
                "Practice fast-response verbal questions on cryptography, DNS attacks, and zero-day defense",
                "Target and apply for 15 curated SOC Analyst, Security Engineer, and AppSec roles"
            ],
            "milestone": "Final TPO Cybersecurity Readiness Clearance & Confirmed Technical Interview Schedule",
            "time_estimate": "10 hours"
        }
    ]

def _build_data_analytics_curriculum(skills: List[str]) -> List[Dict[str, Any]]:
    s0 = skills[0] if len(skills) > 0 else "Advanced SQL & Window Functions"
    s1 = skills[1] if len(skills) > 1 else "Executive Dashboards (Power BI / Tableau)"
    s2 = skills[2] if len(skills) > 2 else "Statistical A/B Testing & KPI Metrics"
    return [
        {
            "week": 1,
            "phase": "Phase 1: Analytical SQL & Data Modeling",
            "title": f"Advanced SQL for Analytics: {s0}",
            "focus": "Window functions (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD), CTEs, and recursive queries.",
            "actions": [
                "Solve 20 complex SQL queries on LeetCode/StrataScratch covering windowing and ranking",
                "Write running totals, moving 7-day averages, and month-over-month growth calculations",
                "Optimize slow queries by analyzing EXPLAIN query execution plans and index usage"
            ],
            "milestone": "Pass advanced SQL benchmark test with 100% correct execution output",
            "time_estimate": "12 hours"
        },
        {
            "week": 2,
            "phase": "Phase 1: Analytical SQL & Data Modeling",
            "title": "Dimensional Modeling & Data Warehousing",
            "focus": "Star schemas, snowflake schemas, fact and dimension tables, and slowly changing dimensions (SCD).",
            "actions": [
                "Design normalized 3NF schema versus star schema optimized for OLAP analytics",
                "Implement fact tables with surrogate keys and degenerate dimensions",
                "Write SQL queries simulating ETL transformation logic from raw staging to analytics mart"
            ],
            "milestone": "Delivered Star Schema ER diagram and analytical datamart DDL scripts",
            "time_estimate": "14 hours"
        },
        {
            "week": 3,
            "phase": "Phase 2: Business Intelligence & Dashboards",
            "title": f"Executive Business Intelligence: {s1}",
            "focus": "Interactive data storytelling, DAX calculations, and executive dashboard design in Power BI / Tableau.",
            "actions": [
                "Build executive sales performance dashboard with drill-down and cross-filtering capabilities",
                "Write complex DAX formulas (CALCULATE, FILTER, time-intelligence functions like YTD/MTD)",
                "Apply UI/UX data visualization best practices (color palette hierarchy, cognitive load reduction)"
            ],
            "milestone": "Published interactive executive dashboard with live KPI cards and trend breakdowns",
            "time_estimate": "15 hours"
        },
        {
            "week": 4,
            "phase": "Phase 2: Business Intelligence & Dashboards",
            "title": "Product Metrics, Funnels & Cohort Analysis",
            "focus": "User retention cohorts, churn analysis, Customer Lifetime Value (LTV), and conversion funnels.",
            "actions": [
                "Perform triangular cohort retention analysis tracking weekly user drop-offs",
                "Construct multi-stage e-commerce checkout conversion funnel identifying drop-off bottlenecks",
                "Calculate customer acquisition cost (CAC), LTV/CAC ratio, and Net Promoter Score (NPS) analytics"
            ],
            "milestone": "Delivered Product Analytics Deck with actionable business recommendations",
            "time_estimate": "15 hours"
        },
        {
            "week": 5,
            "phase": "Phase 3: Python Analytics & Automation",
            "title": "Python for Data Analysis (NumPy, Pandas, Seaborn)",
            "focus": "Automated data ingestion, cleaning, reshaping, and statistical visualization.",
            "actions": [
                "Automate multi-file CSV and Excel consolidation using Pandas read_excel and glob",
                "Perform pivot tables, melt operations, and datetime index manipulations",
                "Generate publication-ready Seaborn and Matplotlib heatmaps and distribution boxplots"
            ],
            "milestone": "Automated data reporting script exporting clean Excel executive summaries with 1 command",
            "time_estimate": "14 hours"
        },
        {
            "week": 6,
            "phase": "Phase 3: Python Analytics & Automation",
            "title": f"Statistical Testing & Experimentation: {s2}",
            "focus": "A/B test design, sample size determination, significance testing, and confidence intervals.",
            "actions": [
                "Calculate required sample sizes using power analysis prior to launching experiments",
                "Run two-sample t-tests and Mann-Whitney U tests on marketing campaign outcomes",
                "Interpret p-values, Type I/II errors, and translate statistical findings into executive language"
            ],
            "milestone": "Complete A/B Test Case Study presentation with statistical validation and business ROI",
            "time_estimate": "14 hours"
        },
        {
            "week": 7,
            "phase": "Phase 4: Portfolio Showcase & Interview Drills",
            "title": "Business Case Studies & Analytical Storytelling",
            "focus": "Translating ambiguous business problems into structured metrics, guesstimates, and root-cause analysis.",
            "actions": [
                "Solve 3 business case studies: 'Why did revenue drop 10% in Q3?' and 'Pricing elasticity optimization'",
                "Practice analytical guesstimates (market sizing) with structured MECE issue trees",
                "Audit portfolio GitHub and Tableau Public profile with executive project summaries"
            ],
            "milestone": "Completed 3 detailed business case study writeups in public portfolio",
            "time_estimate": "14 hours"
        },
        {
            "week": 8,
            "phase": "Phase 4: Portfolio Showcase & Interview Drills",
            "title": "Data Analyst Interview Drills & Placement Drive",
            "focus": "Live SQL whiteboard rounds, business metric defense, and campus placement interviews.",
            "actions": [
                "Complete 10 timed SQL live coding drills under 15-minute constraints",
                "Prepare STAR behavioral narratives focused on influencing stakeholders with data evidence",
                "Target and apply for 15 curated Data Analyst, BI Developer, and Analytics Consultant openings"
            ],
            "milestone": "Final TPO Data Analytics Placement Readiness Clearance & Confirmed Interview Drives",
            "time_estimate": "10 hours"
        }
    ]

def generate_personalized_roadmap(
    student_data: Dict[str, Any],
    missing_skills: List[str],
    target_role: str = "Full-Stack Developer",
    target_lpa: float = 12.0
) -> Dict[str, Any]:
    """
    Generate dynamic, domain-specific 8-week actionable roadmap tailored to
    the student's selected career track / course, incorporating missing skills and LPA tier.
    """
    tier_key = get_lpa_tier(target_lpa)
    tier_info = LPA_BENCHMARK_TIERS[tier_key]
    skills_to_cover = missing_skills if missing_skills else ["Core Algorithms", "System Design", "Cloud Basics"]
    
    track_id = _match_track(target_role)
    
    if track_id == "data_science":
        weeks = _build_data_science_curriculum(skills_to_cover)
        track_title = "Data Science & AI"
        track_icon = "🤖"
    elif track_id == "cloud_devops":
        weeks = _build_cloud_devops_curriculum(skills_to_cover)
        track_title = "Cloud & DevOps"
        track_icon = "☁️"
    elif track_id == "cybersecurity":
        weeks = _build_cybersecurity_curriculum(skills_to_cover)
        track_title = "Cybersecurity"
        track_icon = "🛡️"
    elif track_id == "data_analytics":
        weeks = _build_data_analytics_curriculum(skills_to_cover)
        track_title = "Data Analytics"
        track_icon = "📊"
    else:
        weeks = _build_sde_curriculum(skills_to_cover)
        track_title = "Full-Stack SDE"
        track_icon = "🚀"

    return {
        "track": track_id,
        "track_id": track_id,
        "track_title": track_title,
        "track_icon": track_icon,
        "available_tracks": AVAILABLE_TRACKS,
        "target_role": target_role,
        "target_lpa": target_lpa,
        "tier_info": tier_info,
        "total_weeks": len(weeks),
        "estimated_hours": sum(int(w["time_estimate"].split()[0]) for w in weeks if "time_estimate" in w),
        "weeks": weeks,
        "powered_by": "PlacementAI Domain Curriculum Engine"
    }

"""
Generate professional, ATS-compliant PDF resumes (CVs) for live judge demonstrations.
Generates:
1. static/demo/sample_cv_strong_candidate.pdf (Aarav Sharma - Top Tier SDE Candidate)
2. static/demo/sample_cv_needs_training.pdf (Rahul Kumar - High CGPA with Skill Gaps)
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_strong_cv(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1  # Centered
    )
    
    contact_style = ParagraphStyle(
        'ContactLine',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=3,
        textTransform='uppercase'
    )
    
    item_title_style = ParagraphStyle(
        'ItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a')
    )
    
    item_subtitle_style = ParagraphStyle(
        'ItemSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#1e293b')
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12,
        textColor=colors.HexColor('#334155'),
        leftIndent=12
    )

    story = []

    # Header
    story.append(Paragraph("AARAV SHARMA", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Bengaluru, India • +91 98765 43210 • aarav.sharma@engg.edu • linkedin.com/in/aarav-sharma-dev • github.com/aarav-dev • leetcode.com/aarav_codes", contact_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceBefore=2, spaceAfter=8))

    # Education
    story.append(Paragraph("EDUCATION", section_header_style))
    edu_data = [
        [
            Paragraph("<b>Bangalore Institute of Technology</b> — <i>B.E. in Computer Science & Engineering</i>", item_title_style),
            Paragraph("<b>2022 – 2026</b>", ParagraphStyle('RightText', parent=item_title_style, alignment=2))
        ],
        [
            Paragraph("Semester 7 • <b>CGPA: 8.85 / 10.0</b> • Quantitative Aptitude: 90/100 • Logical Reasoning: 92/100", item_subtitle_style),
            Paragraph("Bengaluru, India", ParagraphStyle('RightSub', parent=item_subtitle_style, alignment=2))
        ]
    ]
    t = Table(edu_data, colWidths=[420, 120])
    t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 1), ('TOPPADDING', (0,0), (-1,-1), 1)]))
    story.append(t)
    story.append(Spacer(1, 6))

    # Technical Skills
    story.append(Paragraph("TECHNICAL SKILLS", section_header_style))
    story.append(Paragraph("<b>Languages & Core:</b> Python (Advanced), Java (Proficient), C++, SQL (PostgreSQL/MySQL), JavaScript, Go", body_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Foundations & Algorithms:</b> Data Structures & Algorithms (DSA), System Design, Object-Oriented Design (OOP), Operating Systems, DBMS", body_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Frameworks & Tools:</b> React.js, FastAPI, Spring Boot, Docker, Redis, Git, Linux CLI, REST APIs, Microservices", body_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Cloud & Infrastructure:</b> AWS (EC2, S3, RDS), Docker Containerization, CI/CD GitHub Actions", body_style))
    story.append(Spacer(1, 8))

    # Experience
    story.append(Paragraph("WORK EXPERIENCE", section_header_style))
    exp_header = [
        [
            Paragraph("<b>Razorpay</b> — <i>Software Engineering Intern (Backend Infrastructure)</i>", item_title_style),
            Paragraph("<b>Jan 2025 – May 2025</b>", ParagraphStyle('R1', parent=item_title_style, alignment=2))
        ]
    ]
    t_exp = Table(exp_header, colWidths=[420, 120])
    t_exp.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    story.append(t_exp)
    story.append(Paragraph("• Architected an asynchronous payment webhook retry queue using Redis and Python Celery, reducing event delivery failures by 38%.", bullet_style))
    story.append(Paragraph("• Implemented idempotent transaction consumer pipelines in FastAPI handling over 140,000 requests/day with sub-80ms p95 latency.", bullet_style))
    story.append(Paragraph("• Integrated OpenTelemetry distributed traces and Prometheus metrics for real-time latency monitoring across 8 microservices.", bullet_style))
    story.append(Spacer(1, 8))

    # Projects
    story.append(Paragraph("FEATURED ENGINEERING PROJECTS", section_header_style))
    
    # Project 1
    p1_header = [
        [
            Paragraph("<b>Distributed Cluster Task Scheduler</b> — <i>Go, Docker, gRPC, Redis, Raft</i>", item_title_style),
            Paragraph("<b>Personal Project</b>", ParagraphStyle('R2', parent=item_title_style, alignment=2))
        ]
    ]
    story.append(Table(p1_header, colWidths=[420, 120], style=[('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    story.append(Paragraph("• Designed a fault-tolerant master-worker distributed job orchestrator executing cron and batch tasks across 5 worker container nodes.", bullet_style))
    story.append(Paragraph("• Implemented Raft consensus heartbeat to ensure automatic master failover within 450ms during network partitions and node crashes.", bullet_style))
    story.append(Paragraph("• Benchmarked worker throughput to process 12,500 tasks per minute with zero task duplication using Redis distributed locks.", bullet_style))
    story.append(Spacer(1, 5))

    # Project 2
    p2_header = [
        [
            Paragraph("<b>PlaceIQ - AI Placement Predictor & Interview Coach</b> — <i>Python, FastAPI, Scikit-Learn, React</i>", item_title_style),
            Paragraph("<b>Hackathon Winner</b>", ParagraphStyle('R3', parent=item_title_style, alignment=2))
        ]
    ]
    story.append(Table(p2_header, colWidths=[420, 120], style=[('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    story.append(Paragraph("• Built a 5-fold cross-validated Stacking Classifier (RF + XGBoost + LightGBM) predicting candidate placement probability with 95.8% accuracy.", bullet_style))
    story.append(Paragraph("• Created real-time conversational AI mock interview room with local Ollama Llama-3.2, WebRTC audio streaming, and SHAP explainability.", bullet_style))
    story.append(Paragraph("• Designed multi-tenant institutional TPO command center managing early warning alerts and cross-job gap analysis across 20+ corporate roles.", bullet_style))
    story.append(Spacer(1, 8))

    # Certifications & Achievements
    story.append(Paragraph("CERTIFICATIONS & COMPETITIVE CODING", section_header_style))
    story.append(Paragraph("• <b>AWS Certified Solutions Architect – Associate</b> (Validation ID: AWS-8492048, Score: 870/1000)", bullet_style))
    story.append(Paragraph("• <b>LeetCode Knight Badge:</b> Solved 380+ Data Structures & Algorithms problems (Rating: 1845, Top 6% globally).", bullet_style))
    story.append(Paragraph("• <b>Smart India Hackathon 2024:</b> Top 10 National Finalist out of 1,200 participating university engineering teams.", bullet_style))
    story.append(Paragraph("• <b>Open Source Contributor:</b> Authored 2 PRs to popular open-source Go microservice tooling.", bullet_style))

    doc.build(story)
    print(f"Created Strong CV: {output_path}")

def create_needs_training_cv(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1
    )
    
    contact_style = ParagraphStyle(
        'ContactLine',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=3,
        textTransform='uppercase'
    )
    
    item_title_style = ParagraphStyle(
        'ItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a')
    )
    
    item_subtitle_style = ParagraphStyle(
        'ItemSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#1e293b')
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12,
        textColor=colors.HexColor('#334155'),
        leftIndent=12
    )

    story = []

    # Header
    story.append(Paragraph("RAHUL KUMAR", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Bengaluru, India • +91 91234 56789 • rahul.kumar@college.edu", contact_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#f59e0b"), spaceBefore=2, spaceAfter=8))

    # Education
    story.append(Paragraph("EDUCATION", section_header_style))
    edu_data = [
        [
            Paragraph("<b>Global Academy of Technology</b> — <i>B.E. in Computer Science & Engineering</i>", item_title_style),
            Paragraph("<b>2022 – 2026</b>", ParagraphStyle('RightText', parent=item_title_style, alignment=2))
        ],
        [
            Paragraph("Semester 7 • <b>CGPA: 8.92 / 10.0</b> • 0 Active Backlogs", item_subtitle_style),
            Paragraph("Bengaluru, India", ParagraphStyle('RightSub', parent=item_subtitle_style, alignment=2))
        ]
    ]
    t = Table(edu_data, colWidths=[420, 120])
    t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 1), ('TOPPADDING', (0,0), (-1,-1), 1)]))
    story.append(t)
    story.append(Spacer(1, 6))

    # Technical Skills (notice: High CGPA but only introductory Python / HTML, 0 DSA, 0 SQL)
    story.append(Paragraph("TECHNICAL SKILLS", section_header_style))
    story.append(Paragraph("<b>Programming Languages:</b> Python (Basic syntax), HTML, CSS", body_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Tools:</b> VS Code, MS Office, Windows, Basic Git commands", body_style))
    story.append(Spacer(1, 8))

    # Projects
    story.append(Paragraph("ACADEMIC PROJECTS", section_header_style))
    p1_header = [
        [
            Paragraph("<b>Personal Portfolio Website</b> — <i>HTML, CSS</i>", item_title_style),
            Paragraph("<b>Academic Project</b>", ParagraphStyle('R2', parent=item_title_style, alignment=2))
        ]
    ]
    story.append(Table(p1_header, colWidths=[420, 120], style=[('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    story.append(Paragraph("• Built a responsive personal portfolio website showcasing coursework and academic certificates.", bullet_style))
    story.append(Paragraph("• Styled using custom CSS with navigation bar and contact form.", bullet_style))
    story.append(Spacer(1, 8))

    # Extra Curriculars
    story.append(Paragraph("COLLEGE ACTIVITIES & SEMINARS", section_header_style))
    story.append(Paragraph("• Member of College Cultural Club organizing annual cultural fest events.", bullet_style))
    story.append(Paragraph("• Attended 2-day workshop on Cloud Computing Introduction.", bullet_style))

    doc.build(story)
    print(f"Created Needs Training CV: {output_path}")

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "static" / "demo"
    out_dir.mkdir(parents=True, exist_ok=True)
    create_strong_cv(str(out_dir / "sample_cv_strong_candidate.pdf"))
    create_needs_training_cv(str(out_dir / "sample_cv_needs_training.pdf"))

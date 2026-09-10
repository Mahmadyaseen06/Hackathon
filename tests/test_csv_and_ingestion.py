import io
import pytest
from fastapi.testclient import TestClient
from api.main import app
from auth import login_student, login_tpo, get_student_by_usn, update_student_profile, batch_upsert_students

client = TestClient(app)


def test_profile_update_and_persistence():
    student = get_student_by_usn("4JN25CS001")
    assert student is not None

    updates = {
        "cgpa": 9.1,
        "quantitative_aptitude": 90.0,
        "skills": {"Python": 9.0, "DSA": 9.0, "SQL": 8.0, "Docker": 8.0}
    }
    updated = update_student_profile("4JN25CS001", updates)
    assert updated["cgpa"] == 9.1
    assert updated["skills"]["Docker"] == 8.0

    # Verify retrieval
    refetched = get_student_by_usn("4JN25CS001")
    assert refetched["cgpa"] == 9.1
    assert refetched["quantitative_aptitude"] == 90.0


def test_batch_upsert_students():
    new_cohort = [
        {
            "usn": "4JN25CS999",
            "name": "Ingestion Unit Test",
            "branch": "Computer Science & Engineering",
            "cgpa": 8.5,
            "semester": 7,
            "active_backlogs": 0,
            "skills": {"Python": 8.0, "DSA": 8.0},
            "internships": ["Tech Corp:Intern:3"],
            "certifications": ["AWS Practitioner"],
            "projects": ["Test Engine"]
        }
    ]
    count = batch_upsert_students(new_cohort)
    assert count == 1
    stu = get_student_by_usn("4JN25CS999")
    assert stu is not None
    assert stu["name"] == "Ingestion Unit Test"


def test_student_csv_upload_api():
    student = login_student("4JN25CS001", "pass@001")
    assert student is not None
    from auth import create_session_token
    token = create_session_token("4JN25CS001", "student")

    csv_content = (
        "cgpa,semester,active_backlogs,quantitative_aptitude,coding_benchmark,communication_rating,skills,certifications,projects,internships\n"
        "8.95,7,0,88,85,8.2,\"Python:9,DSA:8,SQL:8,Kubernetes:7\",\"AWS Solution Architect\",\"Cluster Manager\",\"Stripe:Intern:6\"\n"
    )
    files = {"file": ("profile.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"usn": "4JN25CS001", "token": token}

    response = client.post("/api/student/upload-csv", data=data, files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert "skills" in res_data["updated_fields"]

    # Verify student reflects new data
    stu = get_student_by_usn("4JN25CS001")
    assert stu["cgpa"] == 8.95
    assert stu["skills"].get("Kubernetes") == 7.0


def test_tpo_batch_upload_api():
    tpo_user = login_tpo("TPO-001", "tpo@admin")
    assert tpo_user is not None
    from auth import create_session_token
    token = create_session_token("TPO-001", "tpo")

    batch_csv = (
        "usn,name,branch,cgpa,semester,active_backlogs,quantitative_aptitude,coding_benchmark,communication_rating,skills,internship,certification,project\n"
        "4JN25AI888,AI Student Test,Artificial Intelligence & Machine Learning,9.0,7,0,90,88,8.5,\"Python:9,PyTorch:8,DSA:8\",OpenAI:Intern:6,TensorFlow Dev,Vision App\n"
    )
    files = {"file": ("cohort.csv", io.BytesIO(batch_csv.encode("utf-8")), "text/csv")}
    data = {"token": token}

    response = client.post("/api/tpo/upload-csv", data=data, files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["imported_count"] >= 1

    # Verify student appears in institutional query
    stu = get_student_by_usn("4JN25AI888")
    assert stu is not None
    assert stu["branch"] == "Artificial Intelligence & Machine Learning"


def test_student_and_tpo_csv_upload_with_windows_excel_bom():
    """Verify that Excel CSVs with UTF-8 BOM (\ufeff) are decoded seamlessly without corrupting header keys."""
    from auth import create_session_token

    # 1. Student BOM CSV
    token_stu = create_session_token("4JN25CS001", "student")
    bom_csv = (
        "cgpa,semester,active_backlogs,coding_benchmark,skills\n"
        "9.25,7,0,92,\"Python:9,Go:8,Docker:8\"\n"
    )
    # Encode with utf-8-sig to explicitly prepend the 3-byte \xef\xbb\xbf BOM marker
    bom_bytes = bom_csv.encode("utf-8-sig")
    assert bom_bytes.startswith(b"\xef\xbb\xbf")

    files = {"file": ("excel_bom.csv", io.BytesIO(bom_bytes), "text/csv")}
    resp = client.post("/api/student/upload-csv", data={"usn": "4JN25CS001", "token": token_stu}, files=files)
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    updated_stu = get_student_by_usn("4JN25CS001")
    assert updated_stu["cgpa"] == 9.25
    assert updated_stu["skills"].get("Go") == 8.0

    # 2. TPO BOM CSV
    token_tpo = create_session_token("TPO-001", "tpo")
    tpo_bom_csv = (
        "usn,name,branch,cgpa,semester,active_backlogs,skills\n"
        "4JN25BOM001,BOM Encoded Student,Computer Science & Engineering,8.8,7,0,\"Python:8,DSA:8\"\n"
    )
    tpo_bom_bytes = tpo_bom_csv.encode("utf-8-sig")
    tpo_files = {"file": ("cohort_excel_bom.csv", io.BytesIO(tpo_bom_bytes), "text/csv")}
    tpo_resp = client.post("/api/tpo/upload-csv", data={"token": token_tpo}, files=tpo_files)
    assert tpo_resp.status_code == 200
    assert tpo_resp.json()["success"] is True

    imported_bom_stu = get_student_by_usn("4JN25BOM001")
    assert imported_bom_stu is not None
    assert imported_bom_stu["name"] == "BOM Encoded Student"

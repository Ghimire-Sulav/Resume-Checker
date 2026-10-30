import io

from database.models import Analysis, db


def test_homepage_and_required_pages_load(client):
    for path in ("/", "/dashboard", "/upload", "/about"):
        assert client.get(path).status_code == 200


def test_pasted_resume_analysis_is_saved_and_report_downloads(client, app):
    source_text = (
        "Education\nExample University\nSkills\nPython SQL Teamwork\n"
        "Projects\nStudent data dashboard"
    )
    response = client.post("/upload", data={
        "resume_text": source_text,
        "target_role": "Data Analyst",
    }, follow_redirects=False)
    assert response.status_code == 302
    location = response.headers["Location"]
    page = client.get(location)
    assert page.status_code == 200
    assert b"Demo analysis" in page.data
    assert b"Gemini API key is not configured" in page.data
    assert b"Skills analysis" in page.data
    with app.app_context():
        record = db.session.query(Analysis).one()
        assert record.analysis_mode == "demo"
        assert source_text not in record.analysis_json
        assert "resume_text" not in Analysis.__table__.columns
    report = client.get(location + "/report")
    assert report.status_code == 200
    assert report.headers["Content-Disposition"].startswith("attachment;")
    assert b"RESUME ANALYSIS REPORT" in report.data
    pdf = client.get(location + "/report.pdf")
    assert pdf.status_code == 200
    assert pdf.content_type == "application/pdf"
    assert pdf.data.startswith(b"%PDF-")


def test_full_resume_sections_render_in_results(client):
    sample = """Career Objective: Seeking a backend internship
Academic Background
- BSc Computer Science, Example University
Technical Skills
- Python, Flask, SQL
Personal Projects
- Built a student portal with Flask
Internship Experience
- Backend intern at Example Company
Certifications
- AWS Cloud Practitioner
Soft Skills
- Teamwork, communication"""
    response = client.post(
        "/upload",
        data={"resume_text": sample},
        follow_redirects=True,
    )
    assert response.status_code == 200
    for text in (
        "Seeking a backend internship",
        "BSc Computer Science, Example University",
        "Built a student portal with Flask",
        "Backend intern at Example Company",
        "AWS Cloud Practitioner",
        "Technical skills",
        "Python",
        "Teamwork",
        "Role recommendations",
    ):
        assert text.encode() in response.data


def test_upload_txt(app, client):
    response = client.post("/upload", data={
        "resume_file": (io.BytesIO(b"Python engineer project"), "resume.txt"),
    }, content_type="multipart/form-data")
    assert response.status_code == 302
    with app.app_context():
        record = db.session.query(Analysis).one()
        assert record.original_filename == "resume.txt"
        assert "Python engineer" not in record.analysis_json


def test_empty_and_invalid_uploads_are_rejected(client):
    empty = client.post("/upload", data={"resume_text": ""}, follow_redirects=True)
    assert b"Choose a resume file or paste" in empty.data
    invalid = client.post("/upload", data={
        "resume_file": (io.BytesIO(b"bad"), "resume.exe"),
    }, content_type="multipart/form-data", follow_redirects=True)
    assert b"Upload a PDF, DOCX, or TXT file." in invalid.data


def test_unknown_analysis_returns_404(client):
    assert client.get("/analysis/999").status_code == 404


def test_learning_page_shows_suggestions(client):
    response = client.post("/upload", data={
        "resume_text": "Python projects",
        "target_role": "Data Analyst",
    }, follow_redirects=False)
    results_url = response.headers["Location"]
    learning = client.get(results_url + "/learning")
    assert learning.status_code == 200
    assert b"learning" in learning.data.lower()

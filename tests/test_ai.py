import json

import pytest
import requests

from services.ai_analyzer import AnalysisError, analyze_resume, demo_analysis, validate_analysis
from services.resume_parser import extract_resume_sections


def test_demo_analysis_produces_all_required_fields():
    result = demo_analysis("Python SQL teamwork projects", "Data Analyst")
    assert result["technical_skills"] == ["Python", "SQL"]
    assert result["soft_skills"] == ["Teamwork"]
    assert len(result["job_recommendations"]) == 5
    assert "Data Analyst" in {role["job_title"] for role in result["job_recommendations"]}
    assert isinstance(result["missing_skills"], list)
    assert isinstance(result["learning_suggestions"], list)
    assert isinstance(result["resume_improvements"], list)
    assert isinstance(result["achievements"], list)
    assert result["analysis_notice"].startswith("Rule-based demo")
    analyst = next(
        role for role in result["job_recommendations"]
        if role["job_title"] == "Data Analyst"
    )
    assert analyst["match_percentage"] == round(70 * 2 / 8)


def test_demo_does_not_match_java_inside_javascript():
    result = demo_analysis("JavaScript developer", "Software Engineer")
    assert "JavaScript" in result["technical_skills"]
    assert "Java" not in result["technical_skills"]
    software_role = next(
        role for role in result["job_recommendations"]
        if role["job_title"] == "Software Engineer"
    )
    assert "Java" in software_role["missing_skills"]


def test_demo_extracts_section_content_without_heading():
    result = demo_analysis(
        "Education\nExample University\nBSc Computer Science\nProjects\nStudent dashboard",
        "Data Analyst",
    )
    assert result["education"] == ["Example University", "BSc Computer Science"]
    assert result["projects"] == ["Student dashboard"]


def test_extracts_resume_headings_aliases_case_and_bullets():
    sample = """Career Objective: Seeking a software engineering internship
ACADEMIC BACKGROUND
- BSc Computer Science, Example University, 2022-2026
TECHNICAL SKILLS:
Programming: Python, Java, JavaScript
Tools: Git, Docker
PERSONAL PROJECTS
• Built a student portal with Flask and SQLite
Internship Experience:
- Software Intern at Example Labs, June-August 2025
Certifications
AWS Cloud Practitioner
Soft Skills:
* Teamwork, communication, problem solving"""
    sections = extract_resume_sections(sample)
    assert sections["career_objective"] == ["Seeking a software engineering internship"]
    assert sections["education"] == ["BSc Computer Science, Example University, 2022-2026"]
    assert sections["technical_skills"] == [
        "Programming: Python, Java, JavaScript",
        "Tools: Git, Docker",
    ]
    assert sections["projects"] == ["Built a student portal with Flask and SQLite"]
    assert sections["experience"] == ["Software Intern at Example Labs, June-August 2025"]
    assert sections["certifications"] == ["AWS Cloud Practitioner"]
    assert sections["soft_skills"] == ["Teamwork, communication, problem solving"]


def test_demo_returns_extracted_sections_and_personalized_role_details():
    sample = """Academic Background
- BSc Computer Science
Professional Experience
- Intern developer
Projects
- Flask and SQL student portal
Technical Skills
- Python, Flask, SQL"""
    result = demo_analysis(sample)
    assert result["education"] == ["BSc Computer Science"]
    assert result["experience"] == ["Intern developer"]
    assert result["projects"] == ["Flask and SQL student portal"]
    assert result["job_recommendations"][0]["match_percentage"] >= 20
    assert result["job_recommendations"][0]["matching_skills"]
    assert result["job_recommendations"][0]["missing_skills"]
    assert result["learning_suggestions"][0]["free_resources"][0]["url"].startswith("https://")


def test_validator_rejects_malformed_response():
    with pytest.raises(AnalysisError, match="invalid 'resume_summary'"):
        validate_analysis({"resume_summary": []})


def test_validator_rejects_out_of_range_match():
    data = demo_analysis("Python")
    data["job_recommendations"][0]["match_percentage"] = 120
    with pytest.raises(AnalysisError, match="invalid match percentage"):
        validate_analysis(data)


def test_gemini_request_is_server_side_and_uses_validated_ai_results(app, monkeypatch):
    model_data = {
        "resume_summary": "Computer science student with a Flask project and internship.",
        "overall_feedback": "The project and internship provide relevant practical evidence.",
        "education": ["BSc Computer Science"],
        "experience": ["Intern developer"],
        "projects": ["Built a Flask student portal"],
        "achievements": [],
        "certifications": [],
        "career_objective": [],
        "technical_skills": ["Python", "Flask", "SQL"],
        "soft_skills": ["Teamwork"],
        "strengths": ["Built a Flask project"],
        "weaknesses": ["Add project outcomes when you can verify them."],
        "job_role_rationale": [
            {"job_title": "Software Engineer", "reason": "The resume lists a Flask project."}
        ],
        "learning_suggestions": [],
        "resume_improvements": [{
            "category": "Project descriptions",
            "suggestion": "Describe the project contribution.",
            "weak_example": "",
            "improved_example": "",
        }],
        "ats_suggestions": ["Use standard section headings."],
    }
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": json.dumps(model_data)}]}}]}

    def fake_post(url, **kwargs):
        captured.update(url=url, **kwargs)
        return FakeResponse()

    monkeypatch.setattr("services.ai_analyzer.requests.post", fake_post)
    with app.app_context():
        app.config["GEMINI_API_KEY"] = "mock-secret"
        result, mode = analyze_resume(
            "Education\nBSc Computer Science\nProfessional Experience\nIntern developer\n"
            "Projects\nBuilt a Flask student portal\nSkills\nPython Flask SQL",
        )

    assert mode == "gemini"
    assert result["resume_summary"].startswith("Computer science student")
    assert result["education"] == ["BSc Computer Science"]
    assert result["experience"] == ["Intern developer"]
    assert result["projects"] == ["Built a Flask student portal"]
    assert len(result["job_recommendations"]) == 5
    assert "key=" not in captured["url"]
    assert captured["headers"]["x-goog-api-key"] == "mock-secret"
    assert "BSc Computer Science" in captured["json"]["contents"][0]["parts"][0]["text"]


def test_gemini_timeout_is_clearly_labeled_demo_fallback(app, monkeypatch):
    def timeout(url, **kwargs):
        assert url.endswith(":generateContent")
        assert kwargs["timeout"] == 45
        raise requests.Timeout()

    monkeypatch.setattr("services.ai_analyzer.requests.post", timeout)
    with app.app_context():
        app.config["GEMINI_API_KEY"] = "mock-secret"
        result, mode = analyze_resume("Education\nBSc Computer Science")

    assert mode == "demo"
    assert "timed out" in result["analysis_notice"]
    assert result["resume_summary"].startswith("Demo analysis")


def test_gemini_http_failure_is_reported_as_demo(app, monkeypatch):
    class FailedResponse:
        status_code = 429

    def fail(url, **kwargs):
        assert url.endswith(":generateContent")
        assert kwargs["headers"]["x-goog-api-key"] == "mock-secret"
        raise requests.HTTPError(response=FailedResponse())

    monkeypatch.setattr("services.ai_analyzer.requests.post", fail)
    with app.app_context():
        app.config["GEMINI_API_KEY"] = "mock-secret"
        result, mode = analyze_resume("Projects\nA small Flask app")

    assert mode == "demo"
    assert "HTTP 429" in result["analysis_notice"]


def test_invalid_gemini_json_is_rejected_and_falls_back(app, monkeypatch):
    class InvalidResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "{broken"}]}}]}

    def invalid_response(url, **kwargs):
        assert url.endswith(":generateContent")
        assert "x-goog-api-key" in kwargs["headers"]
        return InvalidResponse()

    monkeypatch.setattr("services.ai_analyzer.requests.post", invalid_response)
    with app.app_context():
        app.config["GEMINI_API_KEY"] = "mock-secret"
        result, mode = analyze_resume("Projects\nA student portal")

    assert mode == "demo"
    assert "invalid response" in result["analysis_notice"]

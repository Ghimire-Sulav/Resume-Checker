import json
from datetime import timezone

from flask import Blueprint, abort, current_app, flash, make_response, redirect, render_template, request, url_for
from sqlalchemy import desc
from werkzeug.exceptions import RequestEntityTooLarge

from database.models import Analysis, db
from services.ai_analyzer import ROLE_SKILLS, analyze_resume
from services.resume_parser import MAX_RESUME_CHARS, ResumeParseError, parse_resume
from services.report_generator import create_pdf_report, create_text_report


main = Blueprint("main", __name__)
JOB_ROLES = tuple(ROLE_SKILLS)


@main.app_errorhandler(RequestEntityTooLarge)
def handle_large_upload(_error):
    current_app.logger.info("Rejected oversized upload: %s", _error)
    flash("The upload is too large. The maximum file size is 5 MB.", "error")
    return redirect(url_for("main.upload"))


@main.get("/")
def home():
    return render_template("index.html")


@main.get("/dashboard")
def dashboard():
    analyses = Analysis.query.order_by(desc(Analysis.created_at)).limit(10).all()
    return render_template("dashboard.html", analyses=analyses)


@main.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html", job_roles=JOB_ROLES)

    resume_text = request.form.get("resume_text", "").strip()
    uploaded_file = request.files.get("resume_file")
    filename = "Pasted resume"
    if uploaded_file and uploaded_file.filename:
        try:
            resume_text = parse_resume(uploaded_file)
            filename = uploaded_file.filename[:255]
        except ResumeParseError as exc:
            flash(str(exc), "error")
            return redirect(url_for("main.upload"))

    if not resume_text:
        flash("Choose a resume file or paste resume text before analyzing.", "error")
        return redirect(url_for("main.upload"))
    if len(resume_text) > MAX_RESUME_CHARS:
        flash(f"Resume text is too long (maximum {MAX_RESUME_CHARS:,} characters).", "error")
        return redirect(url_for("main.upload"))

    target_role = request.form.get("target_role", "").strip()
    if target_role and target_role not in JOB_ROLES:
        flash("Select a job role from the available options.", "error")
        return redirect(url_for("main.upload"))
    try:
        result, mode = analyze_resume(resume_text, target_role)
        record = Analysis(
            original_filename=filename,
            target_role=target_role,
            analysis_json=json.dumps(result),
            analysis_mode=mode,
        )
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unable to save resume analysis")
        flash("The analysis could not be saved. Please try again.", "error")
        return redirect(url_for("main.upload"))
    return redirect(url_for("main.results", analysis_id=record.id))


@main.get("/analysis/<int:analysis_id>")
def results(analysis_id: int):
    record = db.session.get(Analysis, analysis_id)
    if record is None:
        abort(404)
    analysis = _prepare_analysis(json.loads(record.analysis_json), record.analysis_mode)
    return render_template("results.html", record=record, analysis=analysis)


@main.get("/analysis/<int:analysis_id>/learning")
def learning(analysis_id: int):
    record = db.session.get(Analysis, analysis_id)
    if record is None:
        abort(404)
    analysis = _prepare_analysis(json.loads(record.analysis_json), record.analysis_mode)
    return render_template("learning.html", record=record, suggestions=analysis["learning_suggestions"])


@main.get("/analysis/<int:analysis_id>/report")
def report(analysis_id: int):
    record = db.session.get(Analysis, analysis_id)
    if record is None:
        abort(404)
    created_at = record.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    text = create_text_report(
        _prepare_analysis(json.loads(record.analysis_json), record.analysis_mode),
        created_at,
        record.analysis_mode,
    )
    response = make_response(text)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = f'attachment; filename="resume-analysis-{record.id}.txt"'
    return response


@main.get("/analysis/<int:analysis_id>/report.pdf")
def pdf_report(analysis_id: int):
    record = db.session.get(Analysis, analysis_id)
    if record is None:
        abort(404)
    analysis = _prepare_analysis(json.loads(record.analysis_json), record.analysis_mode)
    pdf = create_pdf_report(analysis, record.created_at, record.analysis_mode)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="resume-analysis-{record.id}.pdf"'
    return response


@main.get("/about")
def about():
    return render_template("about.html")


def _prepare_analysis(data: dict, mode: str) -> dict:
    data.setdefault("overall_feedback", data.get("resume_summary", "Review the analysis for accuracy."))
    for key in (
        "education", "experience", "projects", "achievements", "certifications",
        "career_objective", "technical_skills", "soft_skills", "strengths",
        "weaknesses", "ats_suggestions",
    ):
        data.setdefault(key, [])
    data.setdefault("technical_skill_categories", {"Technical skills": data["technical_skills"]})
    for role in data.get("job_recommendations", []):
        role.setdefault("matching_skills", [])
        role.setdefault("missing_skills", role.get("required_skills", []))
    data["missing_skills"] = [
        item if isinstance(item, dict) else {
            "skill": item,
            "importance": "Medium",
            "job_role": "Recommended roles",
            "why_it_matters": f"{item} appears in the role requirements and was not identified in this resume.",
        }
        for item in data.get("missing_skills", [])
    ]
    for item in data.get("learning_suggestions", []):
        item.setdefault("free_resources", [])
    data["resume_improvements"] = [
        item if isinstance(item, dict) else {
            "category": "Resume",
            "suggestion": item,
            "weak_example": "",
            "improved_example": "",
        }
        for item in data.get("resume_improvements", [])
    ]
    data.setdefault("match_criteria", "Skills and resume evidence are compared as guidance, not hiring probabilities.")
    data.setdefault(
        "analysis_notice",
        "Rule-based demo analysis only; no AI-generated feedback is represented as AI."
        if mode == "demo" else "",
    )
    return data

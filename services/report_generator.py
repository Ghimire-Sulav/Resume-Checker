import io
import unicodedata
from datetime import datetime
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate


def create_text_report(analysis: dict[str, Any], created_at: datetime, mode: str) -> str:
    lines = [
        "RESUME ANALYSIS REPORT",
        f"Generated: {created_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Analysis mode: {mode.upper()}",
        "",
        "SUMMARY",
        analysis["resume_summary"],
        "",
        "OVERALL FEEDBACK",
        analysis.get("overall_feedback", ""),
        "",
    ]
    for label, key in (
        ("Strengths", "strengths"),
        ("Areas to improve", "weaknesses"),
        ("Education", "education"),
        ("Experience", "experience"),
        ("Projects", "projects"),
        ("Achievements", "achievements"),
        ("Certifications", "certifications"),
        ("Career objective", "career_objective"),
        ("Technical skills", "technical_skills"),
        ("Soft skills", "soft_skills"),
    ):
        lines.extend([label.upper(), *[f"- {item}" for item in analysis.get(key, [])], ""])
    lines.append("ROLE RECOMMENDATIONS")
    for item in analysis.get("job_recommendations", []):
        lines.append(
            f"- {item['job_title']} ({item['match_percentage']}%): {item['reason']}"
        )
        lines.append(f"  Matching skills: {', '.join(item.get('matching_skills', []))}")
        lines.append(f"  Missing skills: {', '.join(item.get('missing_skills', []))}")
    lines.extend(["", "MISSING SKILLS"])
    for item in analysis.get("missing_skills", []):
        lines.append(
            f"- {item['skill']} [{item['importance']}, {item['job_role']}]: "
            f"{item['why_it_matters']}"
        )
    lines.extend(["", "LEARNING SUGGESTIONS"])
    for item in analysis.get("learning_suggestions", []):
        lines.append(
            f"- {item['skill']} [{item['level']}, {item['estimated_learning_time']}]: "
            f"{item['recommendation']}"
        )
        lines.extend(
            f"  Free resource: {resource['name']} ({resource['url']})"
            for resource in item.get("free_resources", [])
        )
    lines.extend(["", "RESUME IMPROVEMENTS"])
    for item in analysis.get("resume_improvements", []):
        lines.append(f"- {item['category']}: {item['suggestion']}")
        if item.get("weak_example"):
            lines.append(f"  Current: {item['weak_example']}")
        if item.get("improved_example"):
            lines.append(f"  Suggested: {item['improved_example']}")
    lines.extend(["", "ATS SUGGESTIONS", *[f"- {item}" for item in analysis.get("ats_suggestions", [])]])
    lines.extend(["", f"MATCH CRITERIA: {analysis.get('match_criteria', '')}"])
    return "\n".join(lines)


def create_pdf_report(analysis: dict[str, Any], created_at: datetime, mode: str) -> bytes:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#17213b"),
        alignment=TA_CENTER,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="ReportHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#4665f5"),
        spaceBefore=12,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="ReportBody",
        parent=styles["BodyText"],
        leading=14,
        spaceAfter=5,
    ))

    story = [
        Paragraph("RESUME ANALYSIS REPORT", styles["ReportTitle"]),
        Paragraph(
            f"Generated {escape(created_at.strftime('%Y-%m-%d %H:%M UTC'))} "
            f"&nbsp; | &nbsp; Mode: {escape(mode.upper())}",
            styles["ReportBody"],
        ),
    ]

    def heading(value: str) -> None:
        story.append(Paragraph(escape(value), styles["ReportHeading"]))

    def paragraph(value: str) -> None:
        if value.strip():
            safe_value = escape(_pdf_text(value)).replace("\n", "<br/>")
            story.append(Paragraph(safe_value, styles["ReportBody"]))

    def bullets(values: list[str]) -> None:
        for value in values:
            paragraph(f"- {value}")

    heading("Resume summary")
    paragraph(analysis["resume_summary"])
    heading("Overall feedback")
    paragraph(analysis.get("overall_feedback", ""))
    for label, key in (
        ("Strengths", "strengths"),
        ("Areas to improve", "weaknesses"),
        ("Education", "education"),
        ("Experience", "experience"),
        ("Projects", "projects"),
        ("Achievements", "achievements"),
        ("Certifications", "certifications"),
        ("Career objective", "career_objective"),
        ("Technical skills", "technical_skills"),
        ("Soft skills", "soft_skills"),
    ):
        heading(label)
        bullets(analysis.get(key, []))

    heading("Role recommendations")
    for item in analysis.get("job_recommendations", []):
        paragraph(f"{item['job_title']} - {item['match_percentage']}% transparent skill/evidence match")
        paragraph(item["reason"])
        paragraph(f"Matching skills: {', '.join(item.get('matching_skills', []))}")
        paragraph(f"Missing skills: {', '.join(item.get('missing_skills', []))}")

    heading("Missing skills and learning")
    for item in analysis.get("missing_skills", []):
        paragraph(
            f"{item['skill']} [{item['importance']}; {item['job_role']}]: "
            f"{item['why_it_matters']}"
        )
    for item in analysis.get("learning_suggestions", []):
        paragraph(
            f"{item['skill']} - {item['level']} - {item['estimated_learning_time']}: "
            f"{item['recommendation']}"
        )
        for resource in item.get("free_resources", []):
            paragraph(f"Free resource: {resource['name']} - {resource['url']}")

    heading("Resume improvements")
    for item in analysis.get("resume_improvements", []):
        paragraph(f"{item['category']}: {item['suggestion']}")
        if item.get("weak_example"):
            paragraph(f"Current: {item['weak_example']}")
        if item.get("improved_example"):
            paragraph(f"Suggested: {item['improved_example']}")
    heading("ATS suggestions")
    bullets(analysis.get("ats_suggestions", []))
    heading("Match criteria")
    paragraph(analysis.get("match_criteria", ""))

    output = io.BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Resume Analysis Report",
    )
    document.build(story)
    return output.getvalue()


def _pdf_text(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")

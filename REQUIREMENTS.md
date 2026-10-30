# Requirements Specification

## Purpose and scope

Pathfinder is a local-first resume feedback application for college students. A student provides a resume as PDF, DOCX, TXT, or pasted text and receives a structured review. It is an educational support tool, not a hiring decision system.

## Users and user stories

- As a student, I can submit resume text or a supported document and choose a role or automatic recommendations.
- As a student, I can review summary, extracted skills, role alignment, missing skills, learning ideas, and resume improvement feedback.
- As a student, I can download a report and revisit recent analyses on the same local installation.
- As a student, I can use the app without an AI account through labeled demo mode.

## Functional requirements

1. Accept PDF, DOCX, and TXT uploads up to 5 MB and pasted text up to 30,000 characters.
2. Extract text in memory and reject unsupported, empty, encrypted, unreadable, or overlong input with a clear message.
3. Optionally submit content to Gemini using a server-side API key; do not expose credentials to browser code.
4. Return validated structured fields for summary, education, experience, projects, achievements, technical/soft skills, strengths, role matches, missing skills, learning suggestions, resume improvements, and ATS suggestions.
5. Provide clearly identified heuristic demo output when AI is unconfigured or unavailable.
6. Save result JSON, original filename, selected role, timestamp, and mode to SQLite. Do not store original files or a separate full-text copy; extracted details may remain in the structured analysis.
7. Provide home, dashboard, upload, result, learning, and about pages plus a downloadable report.

## Non-functional requirements

- Responsive, accessible-enough HTML using semantic controls and readable contrast.
- Simple local setup with Python, Flask, SQLite, and documented dependencies.
- Validate inputs and model response; surface upload and persistence errors.
- Keep secrets server-side. Restrict file type and size; never expose resumes publicly.
- Demo use should not require paid services.

## Acceptance criteria

- Supported text documents can be parsed and pasted content analyzed.
- Empty and unsupported uploads receive user-facing errors; a text payload does not appear in persisted analysis records.
- Result pages display each requested category and demo/model source.
- Report downloads with a text attachment.
- Tests cover parsing, routes, result persistence, validation, and demo mode.
- Application starts with or without a Gemini key.

## Limitations

- No login, multi-user access control, admin features, retention scheduler, or cross-device history.
- Demo mode uses keyword matching and a limited fixed role catalog; its scores are simple skill overlap, not predictive.
- PDF extraction is text-based and cannot reliably read scanned images or complex layouts.
- AI output can be inaccurate and must be checked by the student.
- Current app is intended for trusted local development, not public production deployment.

# Testing

## Automated suite

Run `pytest` from the project directory. The test suite uses an in-memory SQLite database and does not require network access or a Gemini API key.

Coverage includes:

- Home, dashboard, upload, and about pages.
- Positive extraction checks for TXT, DOCX, and a text-bearing PDF.
- Unsupported file rejection and empty text rejection.
- Demo structured output, section extraction, skill-boundary matching, and validation of malformed model responses / out-of-range role scores.
- Mocked Gemini success verifies the backend credential header, extracted resume prompt, validated model output, and role scoring. Mocked timeout and HTTP failure verify clearly labeled demo fallback.
- Analysis history persistence without a separate full-text field.
- Results, learning, PDF and text report routes.
- 404 behavior for an unknown result.

## Known gaps

- A live Gemini request is not made in tests; a working API key is required to verify the external provider.
- Browser-level accessibility and responsive visual checks are manual.

## Execution record

- `python -m pytest -q`: **22 passed**.
- `python -m compileall -q .`: completed successfully.
- Gemini success, timeout, HTTP error, and invalid JSON paths are tested with mocked HTTP responses.
- A representative resume fixture was parsed for career objective, academic background, technical skills, projects, internship experience, certifications, and soft skills.
- Live Flask smoke check: pasted the representative resume through `/upload`, verified extracted sections in the result HTML, and received a PDF response from `/analysis/<id>/report.pdf`.

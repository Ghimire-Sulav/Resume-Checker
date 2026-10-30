# API and Page Documentation

This application currently exposes server-rendered HTML routes, rather than a public JSON API.

## `GET /`
Renders the home/feature overview.

## `GET /dashboard`
Renders the 10 most recent saved analyses.

## `GET /upload`
Renders the form. Available roles are Software Engineer, Data Analyst, Web Developer, Machine Learning Engineer, Product Manager, Cloud Engineer, and Cybersecurity Analyst.

## `POST /upload`
Accepts `multipart/form-data`:

- `resume_file`: optional PDF, DOCX, or TXT file; maximum request size is 5 MB.
- `resume_text`: optional pasted text; maximum 30,000 characters.
- `target_role`: optional exact role from the page dropdown.

Provide either a file or non-empty text. A selected file takes precedence over pasted text. Successful requests redirect to `/analysis/<id>`. Invalid input redirects back with a user-facing message.

## `GET /analysis/<id>`
Renders structured analysis for the selected saved record. Returns 404 for an unknown identifier.

## `GET /analysis/<id>/learning`
Renders the learning suggestions saved with the analysis.

## `GET /analysis/<id>/report`
Downloads a UTF-8 `text/plain` attachment.

## `GET /analysis/<id>/report.pdf`
Downloads a generated PDF report.

## `GET /about`
Explains data handling and limitations.

## Gemini response

The backend sends JSON-generation requests to Gemini using the server-side `x-goog-api-key` header and validates the returned structure before saving it. When no API key is configured or a request/response error occurs, the app logs a safe notice and uses explicitly labeled demo mode. Role percentages are calculated locally: required-skill coverage is weighted 70%, with project, experience, and education-or-certification evidence worth 10% each. They are not hiring probabilities. Never put the key in frontend code.

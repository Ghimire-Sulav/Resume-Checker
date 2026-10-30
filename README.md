# Pathfinder Resume Analyzer

A student-focused Flask application that reviews resume content, identifies listed skills, compares them with entry-level role checklists, and suggests next steps. It works without an API key in clearly labeled demo mode and can optionally use Google Gemini.

## Features

- Upload PDF, DOCX, and TXT files, or paste resume text.
- Resume summary, skill analysis, career-role recommendations, skill gaps, learning suggestions, resume and ATS formatting tips.
- Local SQLite analysis history and downloadable PDF or plain-text reports.
- Responsive web UI with dashboard, upload, results, learning, and about pages.
- Uploaded files and separate full-text copies are not retained; only analysis output and limited metadata are saved. The structured analysis may include extracted resume details.

## Setup

1. Install Python 3.10 or later.
2. In this directory, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`. Demo mode works without a key. For genuine Gemini analysis, put your Google Gemini API key in `GEMINI_API_KEY` after reviewing Google's data handling terms. Set a unique `SECRET_KEY` before deployment.
5. Run the app:

   ```powershell
   flask --app app run
   ```

   Or use `python app.py`. Open http://127.0.0.1:5000.

## Configuration

Configuration is read from environment variables (or a local `.env` file when using the Flask CLI): `SECRET_KEY`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `DATABASE_URL`, and `FLASK_DEBUG`. The app defaults to a SQLite file in the project directory. Keep `.env` and database files private.

## Tests

```powershell
pytest
```

Tests use an in-memory SQLite database and do not call the external AI API.

## Privacy and limitations

There are no accounts, authentication, user isolation, or automatic data-expiration features. Anyone with access to the local app/database may be able to view saved analyses. Do not deploy publicly without adding authentication, authorization, CSRF protection, rate limiting, secure production settings, and a retention/deletion policy. When Gemini is enabled, resume text is sent to Google for model processing. If the key is absent or Gemini fails, the app clearly switches to demo mode. Demo skill detection uses text matching and an explicit role checklist; the displayed percentages are a weighted checklist estimate, not hiring probabilities or ATS scores.

## Project resources

- [Requirements](REQUIREMENTS.md)
- [Architecture](ARCHITECTURE.md)
- [API documentation](API_DOCUMENTATION.md)
- [User guide](USER_GUIDE.md)
- [Testing notes](TESTING.md)
- [Production readiness](PRODUCTION_READINESS.md)

## Screenshots

Add screenshots here after launching the application locally.

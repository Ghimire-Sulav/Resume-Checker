# User Guide

1. Start the app using the README setup steps and open `http://127.0.0.1:5000`.
2. Select **Analyze my resume**.
3. Upload a PDF, DOCX, or TXT (up to 5 MB), or paste resume text (up to 30,000 characters).
4. Optionally choose a job role. Leave the dropdown empty to compare against several roles.
5. Submit and review the summary, identified skills, role match estimates, gaps, and improvement suggestions.
6. Open learning suggestions for the next skills to explore, or download a plain-text report.
7. Return to the dashboard to revisit recent analyses saved in the local SQLite database.

## Important

The app does not store the resume file or a separate full-text copy, but does store the structured analysis and source filename in the configured database; extracted analysis details may repeat resume information. Demo matches are keyword-based and simple; AI-generated feedback may also be wrong. Verify all claims and only keep skills on a resume that you can substantiate. Do not use a public deployment for real student resumes until authentication and access controls are implemented.

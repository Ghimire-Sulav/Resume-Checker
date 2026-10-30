from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    original_filename = db.Column(db.String(255), nullable=False, default="Pasted resume")
    target_role = db.Column(db.String(100), nullable=False, default="")
    analysis_json = db.Column(db.Text, nullable=False)
    analysis_mode = db.Column(db.String(20), nullable=False, default="demo")

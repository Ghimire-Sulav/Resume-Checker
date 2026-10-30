import pytest

from app import create_app
from config import Config
from database.models import db


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    GEMINI_API_KEY = ""


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.drop_all()
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

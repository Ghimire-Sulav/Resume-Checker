from __future__ import annotations

from flask import Flask

from config import Config
from database.models import db


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)

    from routes import main

    app.register_blueprint(main)
    with app.app_context():
        db.create_all()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])

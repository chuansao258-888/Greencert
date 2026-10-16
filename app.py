from __future__ import annotations

from flask import Flask

from backend.db import initialise_database
from backend.chain import ChainService
from backend.routes import register_blueprints
from config import Config


# Build the Flask app and attach its chain reader.
def create_app(config: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    app.config["DATABASE_PATH"].parent.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_DIR"].mkdir(parents=True, exist_ok=True)
    initialise_database(app.config["DATABASE_PATH"])
    app.extensions["chain"] = ChainService(app.config)
    register_blueprints(app)
    return app


if __name__ == "__main__":
    create_app().run(debug=True)

from flask import Flask

from .pages import pages_blueprint


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(pages_blueprint)

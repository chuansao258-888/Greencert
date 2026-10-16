from flask import Flask

from .pages import pages_blueprint
from .api_auth import auth_blueprint
from .api_content import content_blueprint
from .api_files import files_blueprint
from .api_records import records_blueprint
from .api_transactions import transactions_blueprint


# Register the page and API routes.
def register_blueprints(app: Flask) -> None:
    app.register_blueprint(pages_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(content_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_blueprint(records_blueprint)
    app.register_blueprint(transactions_blueprint)

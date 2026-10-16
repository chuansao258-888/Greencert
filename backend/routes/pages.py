from flask import Blueprint, render_template


pages_blueprint = Blueprint("pages", __name__)


@pages_blueprint.get("/")
@pages_blueprint.get("/dashboard")
def dashboard():
    return render_template("dashboard.html", page_title="Dashboard")


@pages_blueprint.get("/market")
def market():
    return render_template("market.html", page_title="Market")


@pages_blueprint.get("/account")
def account():
    return render_template("account.html", page_title="Account")

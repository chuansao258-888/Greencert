from flask import Blueprint, render_template


pages_blueprint = Blueprint("pages", __name__)


# Render the public dashboard.
@pages_blueprint.get("/")
@pages_blueprint.get("/dashboard")
def dashboard():
    return render_template("dashboard.html", page_title="Dashboard")


# Render active listings.
@pages_blueprint.get("/market")
def market():
    return render_template("market.html", page_title="Market")


# Render wallet and role controls.
@pages_blueprint.get("/account")
def account():
    return render_template("account.html", page_title="Account")


# Render the application form and review queue.
@pages_blueprint.get("/applications")
def applications():
    return render_template("applications.html", page_title="Applications")


# Render certificates owned by the connected wallet.
@pages_blueprint.get("/my-certificates")
def my_certificates():
    return render_template("my_certificates.html", page_title="My certificates")


# Render the wallet's verified activity.
@pages_blueprint.get("/activity")
def activity():
    return render_template("activity.html", page_title="Activity")


# Render the public read-only certificate integrity audit.
@pages_blueprint.get("/audit")
def audit():
    return render_template("audit.html", page_title="Audit")


# Render a public certificate record and event trail.
@pages_blueprint.get("/certificates/<int:certificate_id>")
def certificate_detail(certificate_id: int):
    return render_template("certificate_detail.html", page_title=f"Certificate #{certificate_id}", certificate_id=certificate_id)

from __future__ import annotations

import hashlib
import secrets
import time
from pathlib import Path

from flask import Blueprint, current_app, g, jsonify, request, send_from_directory

from backend.auth import error, require_session
from backend.db import open_database


files_blueprint = Blueprint("files_api", __name__, url_prefix="/api/files")
ALLOWED_TYPES = {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg"}


# Identify supported files from their header bytes.
def detect_type(data: bytes) -> str | None:
    if data.startswith(b"%PDF-"):
        return "application/pdf"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return None


# Read the wallet role from the configured contract.
def current_role() -> str:
    return current_app.extensions["chain"].role_name(g.wallet_address)


# Save an evidence file and its SHA-256 digest.
@files_blueprint.post("")
@require_session(write=True)
def upload_file():
    if current_role() != "Producer":
        return error("A Producer account is required.", 403, "WRONG_ROLE")
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return error("Select an evidence file.", 400, "FILE_REQUIRED")
    data = uploaded.read()
    if not data or len(data) > current_app.config["MAX_CONTENT_LENGTH"]:
        return error("File must be between 1 byte and 5 MiB.", 413, "FILE_SIZE")
    media_type = detect_type(data)
    if media_type not in ALLOWED_TYPES:
        return error("Only PDF, PNG and JPEG evidence files are accepted.", 415, "FILE_TYPE")

    file_id = secrets.token_urlsafe(12)
    stored_name = f"{secrets.token_hex(16)}{ALLOWED_TYPES[media_type]}"
    upload_path = Path(current_app.config["UPLOAD_DIR"])
    target = upload_path / stored_name
    target.write_bytes(data)
    sha256 = hashlib.sha256(data).hexdigest()
    try:
        with open_database(current_app.config["DATABASE_PATH"]) as database:
            database.execute(
                "INSERT INTO files (id, uploader, original_name, stored_name, sha256, media_type, size, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (file_id, g.wallet_address, uploaded.filename, stored_name, sha256, media_type, len(data), int(time.time())),
            )
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return jsonify({"data": {"fileId": file_id, "sha256": sha256, "size": len(data), "mediaType": media_type}}), 201


# Download evidence owned by the wallet or reviewed by Admin.
@files_blueprint.get("/<file_id>")
@require_session()
def download_file(file_id: str):
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        record = database.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    if not record:
        return error("Evidence file was not found.", 404, "NOT_FOUND")
    if record["uploader"] != g.wallet_address and current_role() != "Admin":
        return error("You cannot access this evidence file.", 403, "FORBIDDEN")
    return send_from_directory(current_app.config["UPLOAD_DIR"], record["stored_name"], as_attachment=True, download_name=record["original_name"])

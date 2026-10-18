from __future__ import annotations

import time

from flask import Blueprint, current_app, g, jsonify, request

from backend.auth import error, require_session
from backend.content import canonicalise, normalise_application, normalise_rejection, normalise_retirement
from backend.db import open_database


content_blueprint = Blueprint("content_api", __name__, url_prefix="/api/content")


# Store canonical metadata for an application.
@content_blueprint.post("")
@require_session(write=True, registered=True)
def create_content():
    payload = request.get_json(silent=True) or {}
    kind = payload.get("kind")
    if kind not in ("application", "rejection", "retirement"):
        return error("Unknown content kind.", 400, "INVALID_KIND")
    chain = current_app.extensions["chain"]
    if kind == "rejection" and chain.role_name(g.wallet_address) != "Admin":
        return error("An Admin account is required.", 403, "WRONG_ROLE")
    body = payload.get("payload")
    if not isinstance(body, dict):
        return error("Application payload is required.", 400, "INVALID_PAYLOAD")
    target = chain.contract_address("certificateRegistry").lower()
    if not target:
        return error("Certificate registry is not configured.", 503, "CHAIN_UNAVAILABLE")
    try:
        if kind == "application":
            proof_file_id = body.get("proofFileId")
            with open_database(current_app.config["DATABASE_PATH"]) as database:
                file_record = database.execute("SELECT * FROM files WHERE id = ?", (proof_file_id,)).fetchone()
            if not file_record or file_record["uploader"] != g.wallet_address:
                return error("Upload evidence with this signed-in wallet first.", 422, "INVALID_EVIDENCE")
            normalised, chain_args = normalise_application(body, file_record["sha256"])
        elif kind == "rejection":
            normalised, chain_args = normalise_rejection(body)
            application = chain.contract("certificateRegistry").functions.getApplication(int(chain_args["applicationId"])).call()
            if application[9] != 1:
                return error("Application is not pending.", 409, "INVALID_STATE")
        else:
            normalised, chain_args = normalise_retirement(body)
            certificate = chain.contract("certificateRegistry").functions.getCertificate(int(chain_args["certificateId"])).call()
            if certificate[3].lower() != g.wallet_address or certificate[6] != 1 or certificate[7]:
                return error("Certificate cannot be retired by this wallet.", 409, "INVALID_STATE")
    except ValueError as exc:
        return error(str(exc), 400, "INVALID_PAYLOAD")

    envelope = {"schemaVersion": 1, "kind": kind, "chainId": current_app.config["CHAIN_ID"], "targetContract": target, "creator": g.wallet_address, "payload": normalised}
    canonical_json, digest = canonicalise(envelope)
    chain_args[{"application": "metadataHash", "rejection": "reasonHash", "retirement": "retirementHash"}[kind]] = digest
    now = int(time.time())
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        exists = database.execute("SELECT 1 FROM contents WHERE content_hash = ?", (digest,)).fetchone()
        if not exists:
            database.execute(
                "INSERT INTO contents (content_hash, kind, creator, chain_id, target_contract, canonical_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (digest, kind, g.wallet_address, current_app.config["CHAIN_ID"], target, canonical_json, now),
            )
            if kind == "application":
                database.execute("INSERT INTO content_files (content_hash, file_id) VALUES (?, ?)", (digest, proof_file_id))
    return jsonify({"data": {"contentHash": digest, "canonicalJson": canonical_json, "chainArgs": chain_args}}), 200 if exists else 201


# Return the exact JSON that was hashed for a content record.
@content_blueprint.get("/<content_hash>")
def get_content(content_hash: str):
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        record = database.execute("SELECT * FROM contents WHERE content_hash = ?", (content_hash,)).fetchone()
    if not record:
        return error("Content was not found.", 404, "NOT_FOUND")
    return jsonify({"data": {"contentHash": record["content_hash"], "canonicalJson": record["canonical_json"]}})

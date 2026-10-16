from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, request
from web3 import Web3

from backend.auth import error, require_session
from backend.db import open_database


records_blueprint = Blueprint("records_api", __name__, url_prefix="/api")


# Return public network and contract settings.
@records_blueprint.get("/config")
def configuration():
    chain = current_app.extensions["chain"]
    return jsonify({"data": {
        "chainId": current_app.config["CHAIN_ID"], "currency": "ETH",
        "contracts": chain.deployment.get("contracts", {}),
        "configured": chain.configured(),
    }})


# Report whether the application can reach its contracts.
@records_blueprint.get("/health")
def health():
    chain = current_app.extensions["chain"]
    return jsonify({"data": {"status": "ready" if chain.configured() else "unconfigured"}}), 200 if chain.configured() else 503


# Return applications visible to the signed-in role.
@records_blueprint.get("/applications")
@require_session()
def applications():
    chain = current_app.extensions["chain"]
    if not chain.configured():
        return error("Contracts are not configured.", 503, "CHAIN_UNAVAILABLE")
    role = chain.role_name(g.wallet_address)
    if role not in ("Producer", "Admin"):
        return error("A Producer or Admin account is required.", 403, "WRONG_ROLE")
    items = chain.applications()
    if role == "Producer":
        items = [item for item in items if item["producer"].lower() == g.wallet_address]
    status = request.args.get("status")
    if status:
        items = [item for item in items if item["status"] == status]
    return jsonify({"data": items})


# Return one application and its stored metadata.
@records_blueprint.get("/applications/<int:application_id>")
@require_session()
def application_detail(application_id: int):
    chain = current_app.extensions["chain"]
    if not chain.configured():
        return error("Contracts are not configured.", 503, "CHAIN_UNAVAILABLE")
    items = chain.applications()
    item = next((entry for entry in items if entry["id"] == str(application_id)), None)
    if not item:
        return error("Application was not found.", 404, "NOT_FOUND")
    if chain.role_name(g.wallet_address) != "Admin" and item["producer"].lower() != g.wallet_address:
        return error("Application is not visible to this wallet.", 403, "FORBIDDEN")
    item["metadata"] = _content(item["metadataHash"])
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        evidence = database.execute("SELECT file_id FROM content_files WHERE content_hash = ?", (item["metadataHash"],)).fetchone()
    item["evidenceFileId"] = evidence["file_id"] if evidence else None
    return jsonify({"data": item})


# Return certificate records with optional public filters.
@records_blueprint.get("/certificates")
def certificates():
    chain = current_app.extensions["chain"]
    if not chain.configured():
        return error("Contracts are not configured.", 503, "CHAIN_UNAVAILABLE")
    items = chain.certificates()
    owner = request.args.get("owner", "").lower()
    if owner:
        items = [item for item in items if item["owner"].lower() == owner]
    status = request.args.get("status")
    if status:
        items = [item for item in items if item["status"] == status]
    if request.args.get("listed") == "true":
        items = [item for item in items if item["listed"]]
    for item in items:
        item["metadata"] = _content(item["metadataHash"])
    return jsonify({"data": items})


# Return one certificate and its immutable content.
@records_blueprint.get("/certificates/<int:certificate_id>")
def certificate_detail(certificate_id: int):
    chain = current_app.extensions["chain"]
    if not chain.configured():
        return error("Contracts are not configured.", 503, "CHAIN_UNAVAILABLE")
    item = next((entry for entry in chain.certificates() if entry["id"] == str(certificate_id)), None)
    if not item:
        return error("Certificate was not found.", 404, "NOT_FOUND")
    item["metadata"] = _content(item["metadataHash"])
    item["retirement"] = _content(item["retirementHash"])
    return jsonify({"data": item})


# Return the on-chain event trail for one certificate.
@records_blueprint.get("/certificates/<int:certificate_id>/events")
def certificate_events(certificate_id: int):
    chain = current_app.extensions["chain"]
    if not chain.configured():
        return error("Contracts are not configured.", 503, "CHAIN_UNAVAILABLE")
    try:
        events = chain.certificate_events(certificate_id)
    except Exception:
        return error("Event history is unavailable from the RPC provider.", 503, "RPC_UNAVAILABLE")
    return jsonify({"data": events})


# Return dashboard totals and chart data from issued certificates.
@records_blueprint.get("/dashboard")
def dashboard():
    chain = current_app.extensions["chain"]
    if not chain.configured():
        return error("Contracts are not configured.", 503, "CHAIN_UNAVAILABLE")
    items = chain.certificates()
    market = chain.contract("certificateMarket")
    source_totals = {source: {"quantity": 0, "batches": 0} for source in ("Solar", "Wind", "Hydro", "Unknown")}
    total_mwh = 0
    for item in items:
        quantity = int(item["quantity"])
        metadata = _content(item["metadataHash"])
        source = metadata.get("source") if metadata else None
        if source not in source_totals:
            source = "Unknown"
        source_totals[source]["quantity"] += quantity
        source_totals[source]["batches"] += 1
        total_mwh += quantity
    return jsonify({"data": {
        "issued": len(items), "active": sum(item["status"] == "Active" for item in items),
        "listed": sum(item["listed"] for item in items),
        "retired": sum(item["status"] == "Retired" for item in items),
        "sold": market.functions.soldCount().call(),
        "totalSalesWei": str(market.functions.totalSalesWei().call()),
        "totalMWh": str(total_mwh),
        "sourceBreakdown": [
            {"source": source, "quantityMWh": str(values["quantity"]), "batches": values["batches"]}
            for source, values in source_totals.items()
        ],
    }})


# Return the signed-in wallet's role and claimable proceeds.
@records_blueprint.get("/wallet")
@require_session()
def wallet():
    chain = current_app.extensions["chain"]
    if not chain.configured():
        return error("Contracts are not configured.", 503, "CHAIN_UNAVAILABLE")
    checksum_address = Web3.to_checksum_address(g.wallet_address)
    balance = chain.web3.eth.get_balance(checksum_address)
    claimable = chain.contract("certificateMarket").functions.credits(checksum_address).call()
    return jsonify({"data": {"address": g.wallet_address, "role": chain.role_name(g.wallet_address), "balanceWei": str(balance), "claimableWei": str(claimable)}})


# Load a saved content envelope by its on-chain hash.
def _content(content_hash: str) -> dict | None:
    if not content_hash or int(content_hash, 16) == 0:
        return None
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        row = database.execute("SELECT canonical_json FROM contents WHERE content_hash = ?", (content_hash,)).fetchone()
    if not row:
        return None
    import json
    return json.loads(row["canonical_json"])["payload"]

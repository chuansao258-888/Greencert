from __future__ import annotations

import time
import re

from flask import Blueprint, current_app, g, jsonify, request

from backend.auth import error, require_session
from backend.db import open_database


transactions_blueprint = Blueprint("transactions_api", __name__, url_prefix="/api/transactions")
METHODS = {
    "register", "submitApplication", "withdrawApplication", "approveApplication", "rejectApplication",
    "listCertificate", "updatePrice", "cancelListing", "buyCertificate", "withdraw", "retireCertificate",
}


# Decode and save a wallet transaction after its receipt is available.
@transactions_blueprint.post("/verify")
@require_session(write=True)
def verify_transaction():
    tx_hash = (request.get_json(silent=True) or {}).get("txHash", "")
    if not isinstance(tx_hash, str) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", tx_hash):
        return error("A transaction hash is required.", 400, "INVALID_HASH")
    chain = current_app.extensions["chain"]
    if not chain.configured():
        return error("Contracts are not configured.", 503, "CHAIN_UNAVAILABLE")
    try:
        transaction, receipt = chain.transaction(tx_hash)
    except Exception:
        return error("Transaction is not available from the RPC provider.", 503, "RPC_UNAVAILABLE")
    if transaction["from"].lower() != g.wallet_address:
        return error("Transaction sender does not match this wallet.", 403, "FORBIDDEN")
    target = (transaction.get("to") or "").lower()
    name = next((key for key in ("roleRegistry", "certificateRegistry", "certificateMarket") if chain.contract_address(key).lower() == target), None)
    if not name:
        return error("Transaction targets a different contract.", 422, "INVALID_TARGET")
    try:
        function, arguments = chain.contract(name).decode_function_input(transaction["input"])
    except Exception:
        return error("Transaction input is not recognized.", 422, "INVALID_METHOD")
    method = function.fn_name
    if method not in METHODS:
        return error("Method is not part of the GreenCert workflow.", 422, "INVALID_METHOD")
    content_hash = next((arguments[key].hex() for key in ("metadataHash", "reasonHash", "retirementHash") if key in arguments), None)
    if content_hash:
        content_hash = "0x" + content_hash.removeprefix("0x")
        with open_database(current_app.config["DATABASE_PATH"]) as database:
            content = database.execute("SELECT * FROM contents WHERE content_hash = ?", (content_hash,)).fetchone()
        expected_kind = {"submitApplication": "application", "rejectApplication": "rejection", "retireCertificate": "retirement"}.get(method)
        if not content or content["creator"] != g.wallet_address or content["kind"] != expected_kind or content["target_contract"] != target:
            return error("Transaction metadata does not match stored content.", 422, "INVALID_CONTENT")
    status = "pending" if receipt is None else "confirmed" if receipt["status"] == 1 else "failed"
    if status == "confirmed" and not any(log["address"].lower() == target for log in receipt["logs"]):
        return error("Expected contract event was not found.", 422, "MISSING_EVENT")
    entity_id = next((str(arguments[key]) for key in ("certificateId", "applicationId") if key in arguments), None)
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        database.execute(
            "INSERT OR REPLACE INTO verified_transactions (chain_id, tx_hash, sender, target, method, entity_type, entity_id, status, value_wei, gas_used, block_number, block_hash, content_hash, verified_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                current_app.config["CHAIN_ID"], tx_hash.lower(), g.wallet_address, target, method,
                "certificate" if "certificateId" in arguments else "application" if "applicationId" in arguments else None,
                entity_id, status, str(transaction["value"]), str(receipt["gasUsed"]) if receipt else None,
                str(receipt["blockNumber"]) if receipt else None, "0x" + receipt["blockHash"].hex().removeprefix("0x") if receipt else None,
                content_hash, int(time.time()),
            ),
        )
    return jsonify({"data": {"txHash": tx_hash.lower(), "method": method, "status": status, "gasUsed": str(receipt["gasUsed"]) if receipt else None}}), 202 if status == "pending" else 200


# Return recent verified transactions for the signed-in wallet.
@transactions_blueprint.get("")
@require_session()
def list_transactions():
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        rows = database.execute("SELECT * FROM verified_transactions WHERE sender = ? ORDER BY verified_at DESC, tx_hash DESC LIMIT 50", (g.wallet_address,)).fetchall()
    return jsonify({"data": [dict(row) for row in rows]})


# Return one saved transaction owned by the signed-in wallet.
@transactions_blueprint.get("/<tx_hash>")
@require_session()
def transaction_detail(tx_hash: str):
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        row = database.execute("SELECT * FROM verified_transactions WHERE tx_hash = ? AND sender = ?", (tx_hash.lower(), g.wallet_address)).fetchone()
    if not row:
        return error("Transaction was not found.", 404, "NOT_FOUND")
    return jsonify({"data": dict(row)})

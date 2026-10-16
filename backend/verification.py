from __future__ import annotations

import hashlib
import json
from pathlib import Path

from eth_utils import keccak

from backend.content import content_hash
from backend.db import open_database


def evidence_report(certificate: dict, application: dict | None, database_path: Path, upload_dir: Path, chain_id: int, registry_address: str) -> dict:
    """Check recorded hashes and links without publishing the uploaded file."""
    linked = bool(application and all((
        application["status"] == "Approved",
        application["certificateId"] == certificate["id"],
        application["producer"].lower() == certificate["producer"].lower(),
        application["quantity"] == certificate["quantity"],
        application["metadataHash"].lower() == certificate["metadataHash"].lower(),
    )))
    checks = {"approvedApplication": "passed" if linked else "failed"}
    with open_database(database_path) as database:
        content = database.execute(
            "SELECT canonical_json FROM contents WHERE content_hash = ?", (certificate["metadataHash"],)
        ).fetchone()
        file_record = database.execute(
            "SELECT files.* FROM content_files JOIN files ON files.id = content_files.file_id WHERE content_files.content_hash = ?",
            (certificate["metadataHash"],),
        ).fetchone()

    payload = None
    if content is None:
        checks["metadataHash"] = "unavailable"
        checks["metadataFields"] = "unavailable"
    elif content_hash(content["canonical_json"]).lower() != certificate["metadataHash"].lower():
        checks["metadataHash"] = "failed"
        checks["metadataFields"] = "unavailable"
    else:
        checks["metadataHash"] = "passed"
        try:
            envelope = json.loads(content["canonical_json"])
            payload = envelope["payload"]
            site_hash = "0x" + keccak(text=payload["siteCode"]).hex()
            fields_match = bool(application and all((
                envelope["kind"] == "application",
                int(envelope["chainId"]) == chain_id,
                envelope["creator"].lower() == certificate["producer"].lower(),
                envelope["targetContract"].lower() == registry_address.lower(),
                site_hash.lower() == application["siteHash"].lower(),
                str(payload["periodStart"]) == application["periodStart"],
                str(payload["periodEnd"]) == application["periodEnd"],
                str(payload["batchIndex"]) == application["batchIndex"],
                str(payload["quantity"]) == certificate["quantity"],
            )))
            checks["metadataFields"] = "passed" if fields_match else "failed"
        except (KeyError, TypeError, ValueError, AttributeError):
            checks["metadataFields"] = "failed"
            payload = None

    if file_record is None:
        checks["evidenceFile"] = "unavailable"
    else:
        stored_name = file_record["stored_name"]
        path = upload_dir / stored_name
        if Path(stored_name).name != stored_name:
            checks["evidenceFile"] = "failed"
        elif not path.is_file():
            checks["evidenceFile"] = "unavailable"
        elif payload is None:
            checks["evidenceFile"] = "unavailable"
        else:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            checks["evidenceFile"] = "passed" if all((
                file_record["uploader"].lower() == certificate["producer"].lower(),
                digest == file_record["sha256"],
                digest == payload.get("proofSha256"),
            )) else "failed"

    states = set(checks.values())
    status = "mismatch" if "failed" in states else "incomplete" if "unavailable" in states else "verified"
    summary = None
    if payload is not None and checks["metadataFields"] == "passed":
        summary = {key: payload.get(key) for key in (
            "siteCode", "siteName", "source", "country", "periodStart", "periodEnd", "batchIndex", "quantity", "proofSha256"
        )}
    return {
        "certificateId": certificate["id"], "applicationId": certificate["applicationId"],
        "status": status, "checks": checks, "summary": summary,
        "metadataHash": certificate["metadataHash"],
    }

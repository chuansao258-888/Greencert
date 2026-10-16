from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from eth_utils import keccak


SITE_CODE = re.compile(r"^[A-Z0-9-]{1,40}$")
SOURCES = {"Solar", "Wind", "Hydro"}


# Hash the exact canonical JSON stored by the server.
def content_hash(canonical_json: str) -> str:
    return "0x" + keccak(text=canonical_json).hex()


# Serialize metadata in a stable field order.
def canonicalise(envelope: dict) -> tuple[str, str]:
    canonical_json = json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return canonical_json, content_hash(canonical_json)


# Validate a required text field.
def _text(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} is required.")
    value = value.strip()
    if not value or len(value) > maximum or any(ord(character) < 32 for character in value):
        raise ValueError(f"{label} is invalid.")
    return value


# Validate application metadata and derive contract arguments.
def normalise_application(payload: dict, proof_sha256: str) -> tuple[dict, dict]:
    site_code = _text(payload.get("siteCode"), "Site code", 40).upper()
    if not SITE_CODE.fullmatch(site_code):
        raise ValueError("Site code may contain uppercase letters, digits and hyphens only.")
    source = payload.get("source")
    if source not in SOURCES:
        raise ValueError("Source must be Solar, Wind or Hydro.")
    country = _text(payload.get("country"), "Country", 2).upper()
    if not re.fullmatch(r"[A-Z]{2}", country):
        raise ValueError("Country must be a two-letter code.")
    try:
        values = [payload.get(key) for key in ("periodStart", "periodEnd", "batchIndex", "quantity")]
        if any(isinstance(value, bool) or not str(value).isdigit() for value in values):
            raise ValueError("Numeric fields must be non-negative integers.")
        period_start, period_end, batch_index, quantity = map(int, values)
    except (TypeError, ValueError) as error:
        raise ValueError("Period, batch index and quantity must be numbers.") from error
    if period_start <= 0 or period_start >= period_end or period_end > int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Generation period is invalid.")
    if not 0 < batch_index <= 2**32 - 1 or not 1 <= quantity <= 100:
        raise ValueError("Batch index or quantity is outside the allowed range.")
    normalised = {
        "siteCode": site_code,
        "siteName": _text(payload.get("siteName"), "Site name", 80),
        "source": source,
        "country": country,
        "periodStart": str(period_start),
        "periodEnd": str(period_end),
        "batchIndex": str(batch_index),
        "quantity": str(quantity),
        "energyMWh": str(quantity),
        "proofSha256": proof_sha256,
    }
    chain_args = {
        "siteHash": "0x" + keccak(text=site_code).hex(),
        "periodStart": str(period_start),
        "periodEnd": str(period_end),
        "batchIndex": str(batch_index),
        "quantity": str(quantity),
    }
    return normalised, chain_args


# Validate a review reason and derive its contract hash.
def normalise_rejection(payload: dict) -> tuple[dict, dict]:
    application_id = _positive_id(payload.get("applicationId"), "Application ID")
    reason = _text(payload.get("reason"), "Reason", 500)
    return {"applicationId": str(application_id), "reason": reason}, {"applicationId": str(application_id)}


# Validate a retirement statement and derive its contract hash.
def normalise_retirement(payload: dict) -> tuple[dict, dict]:
    certificate_id = _positive_id(payload.get("certificateId"), "Certificate ID")
    beneficiary = _text(payload.get("beneficiary"), "Beneficiary", 100)
    purpose = _text(payload.get("purpose"), "Purpose", 500)
    return {"certificateId": str(certificate_id), "beneficiary": beneficiary, "purpose": purpose}, {"certificateId": str(certificate_id)}


# Parse a positive decimal identifier.
def _positive_id(value: object, label: str) -> int:
    if isinstance(value, bool) or not str(value).isdigit() or int(value) <= 0:
        raise ValueError(f"{label} must be a positive integer.")
    return int(value)

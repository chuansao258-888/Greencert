from __future__ import annotations

import hashlib
import secrets
import time
from functools import wraps

from eth_account import Account
from eth_account.messages import encode_defunct
from flask import current_app, g, jsonify, request
from web3 import Web3

from .db import open_database


SESSION_COOKIE = "greencert_session"


# Return a consistent API error body.
def error(message: str, status: int, code: str = "REQUEST_ERROR"):
    return jsonify({"error": {"code": code, "message": message}}), status


# Validate and normalize a wallet address.
def normalise_address(value: str) -> str:
    if not isinstance(value, str) or not Web3.is_address(value):
        raise ValueError("A valid wallet address is required.")
    return value.lower()


# Save a short-lived message for wallet sign-in.
def create_challenge(address: str) -> dict:
    now = int(time.time())
    nonce = secrets.token_urlsafe(24)
    expires_at = now + 300
    message = "\n".join((
        "GreenCert wallet sign-in",
        f"Origin: {current_app.config['APP_ORIGIN']}",
        f"Chain ID: {current_app.config['CHAIN_ID']}",
        f"Address: {address}",
        f"Nonce: {nonce}",
        f"Issued at: {now}",
        f"Expires at: {expires_at}",
    ))
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        database.execute(
            "INSERT INTO auth_challenges (nonce, address, message, issued_at, expires_at) VALUES (?, ?, ?, ?, ?)",
            (nonce, address, message, now, expires_at),
        )
    return {"nonce": nonce, "message": message, "expiresAt": expires_at}


# Verify the wallet signature and create a session.
def verify_challenge(address: str, nonce: str, signature: str) -> dict:
    now = int(time.time())
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        challenge = database.execute("SELECT * FROM auth_challenges WHERE nonce = ?", (nonce,)).fetchone()
        if not challenge or challenge["address"] != address or challenge["consumed_at"] is not None or challenge["expires_at"] < now:
            raise ValueError("The sign-in challenge is invalid or expired.")
        recovered = Account.recover_message(encode_defunct(text=challenge["message"]), signature=signature).lower()
        if recovered != address:
            raise ValueError("The signature does not match this wallet.")
        database.execute("UPDATE auth_challenges SET consumed_at = ? WHERE nonce = ?", (now, nonce))
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        csrf_token = secrets.token_urlsafe(24)
        expires_at = now + 8 * 60 * 60
        database.execute(
            "INSERT INTO sessions (token_hash, address, csrf_token, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
            (token_hash, address, csrf_token, now, expires_at),
        )
    return {"token": raw_token, "address": address, "csrfToken": csrf_token, "expiresAt": expires_at}


# Read the current unexpired wallet session.
def session_from_request():
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        session = database.execute("SELECT * FROM sessions WHERE token_hash = ?", (token_hash,)).fetchone()
    if not session or session["expires_at"] < int(time.time()):
        return None
    return session


# Require a wallet session and a CSRF token for writes.
def require_session(write: bool = False):
    # Wrap a route with the shared authentication checks.
    def decorator(view):
        # Resolve the session before running the route.
        @wraps(view)
        def wrapped(*args, **kwargs):
            session = session_from_request()
            if not session:
                return error("Sign in with your wallet first.", 401, "AUTH_REQUIRED")
            if write:
                origin = request.headers.get("Origin")
                csrf_token = request.headers.get("X-CSRF-Token")
                if origin and origin != current_app.config["APP_ORIGIN"]:
                    return error("The request origin is not allowed.", 403, "INVALID_ORIGIN")
                if csrf_token != session["csrf_token"]:
                    return error("A valid CSRF token is required.", 403, "INVALID_CSRF")
            g.wallet_address = session["address"]
            g.session = session
            return view(*args, **kwargs)
        return wrapped
    return decorator


# Remove the current wallet session.
def revoke_current_session() -> None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with open_database(current_app.config["DATABASE_PATH"]) as database:
        database.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))

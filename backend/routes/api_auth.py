from flask import Blueprint, current_app, g, jsonify, make_response, request

from backend.auth import SESSION_COOKIE, create_challenge, error, normalise_address, require_session, revoke_current_session, verify_challenge


auth_blueprint = Blueprint("auth_api", __name__, url_prefix="/api/auth")


# Create a sign-in challenge for the supplied wallet.
@auth_blueprint.post("/challenge")
def challenge():
    try:
        address = normalise_address((request.get_json(silent=True) or {}).get("address"))
        return jsonify({"data": create_challenge(address)})
    except ValueError as exc:
        return error(str(exc), 400, "INVALID_ADDRESS")


# Exchange a wallet signature for a session.
@auth_blueprint.post("/verify")
def verify():
    payload = request.get_json(silent=True) or {}
    try:
        address = normalise_address(payload.get("address"))
        session = verify_challenge(address, payload.get("nonce", ""), payload.get("signature", ""))
        role = current_app.extensions["chain"].role_name(address)
    except ValueError as exc:
        return error(str(exc), 401, "INVALID_SIGNATURE")
    response = make_response(jsonify({"data": {key: value for key, value in session.items() if key != "token"} | {"role": role}}))
    response.set_cookie(
        SESSION_COOKIE,
        session["token"],
        max_age=8 * 60 * 60,
        httponly=True,
        samesite="Lax",
        secure=current_app.config["COOKIE_SECURE"],
    )
    return response


# Return the signed-in wallet and its role.
@auth_blueprint.get("/me")
@require_session()
def me():
    return jsonify({"data": {
        "address": g.wallet_address,
        "role": current_app.extensions["chain"].role_name(g.wallet_address),
        "csrfToken": g.session["csrf_token"],
        "expiresAt": g.session["expires_at"],
    }})


# End the current wallet session.
@auth_blueprint.post("/logout")
@require_session(write=True)
def logout():
    revoke_current_session()
    response = make_response(jsonify({"data": {"loggedOut": True}}))
    response.delete_cookie(SESSION_COOKIE)
    return response

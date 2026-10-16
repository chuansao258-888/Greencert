from eth_account import Account
from eth_account.messages import encode_defunct

from tests.backend.base import AppTestCase


class AuthTests(AppTestCase):
    # Authenticate with a signed challenge and reject reuse.
    def test_wallet_sign_in_and_replay(self) -> None:
        wallet = Account.create()
        challenge = self.client.post("/api/auth/challenge", json={"address": wallet.address}).json["data"]
        signature = Account.sign_message(encode_defunct(text=challenge["message"]), wallet.key).signature.hex()
        payload = {"address": wallet.address, "nonce": challenge["nonce"], "signature": signature}
        response = self.client.post("/api/auth/verify", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["address"], wallet.address.lower())
        self.assertEqual(self.client.get("/api/auth/me").status_code, 200)
        self.assertEqual(self.client.post("/api/auth/verify", json=payload).status_code, 401)

    # Require a matching signature for wallet sign-in.
    def test_wrong_wallet_signature(self) -> None:
        wallet = Account.create()
        challenge = self.client.post("/api/auth/challenge", json={"address": wallet.address}).json["data"]
        signature = Account.sign_message(encode_defunct(text=challenge["message"]), Account.create().key).signature.hex()
        response = self.client.post("/api/auth/verify", json={"address": wallet.address, "nonce": challenge["nonce"], "signature": signature})
        self.assertEqual(response.status_code, 401)

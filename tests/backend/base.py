from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from eth_account import Account
from eth_account.messages import encode_defunct

from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"


class AppTestCase(TestCase):
    # Create an isolated database and upload folder for each test.
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        root = Path(self.temporary_directory.name)

        class LocalConfig(TestConfig):
            DATABASE_PATH = root / "test.db"
            UPLOAD_DIR = root / "uploads"

        self.app = create_app(LocalConfig)
        self.client = self.app.test_client()

    # Remove temporary test data after each test.
    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    # Sign in with a fresh local wallet and return its CSRF token.
    def sign_in(self) -> tuple[str, str]:
        wallet = Account.create()
        challenge = self.client.post("/api/auth/challenge", json={"address": wallet.address}).json["data"]
        signature = Account.sign_message(encode_defunct(text=challenge["message"]), wallet.key).signature.hex()
        response = self.client.post("/api/auth/verify", json={"address": wallet.address, "nonce": challenge["nonce"], "signature": signature})
        return wallet.address.lower(), response.json["data"]["csrfToken"]

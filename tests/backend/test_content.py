import json
from io import BytesIO
from datetime import datetime, timezone

from eth_utils import keccak

from backend.content import canonicalise, normalise_application, normalise_rejection, normalise_retirement
from tests.backend.base import AppTestCase


class ContentTests(AppTestCase):
    # Keep canonical hashes stable across dictionary field order.
    def test_canonical_hash(self) -> None:
        first, digest = canonicalise({"b": 2, "a": 1})
        second, second_digest = canonicalise({"a": 1, "b": 2})
        self.assertEqual(first, second)
        self.assertEqual(digest, second_digest)
        self.assertEqual(digest, "0x" + keccak(text=first).hex())

    # Accept a multi-unit batch and derive its contract arguments.
    def test_application_quantity(self) -> None:
        now = int(datetime.now(timezone.utc).timestamp())
        payload = {"siteCode": "solar-01", "siteName": "Demo site", "source": "Solar", "country": "sg", "periodStart": str(now - 3600), "periodEnd": str(now - 60), "batchIndex": "1", "quantity": "25"}
        normalised, args = normalise_application(payload, "a" * 64)
        self.assertEqual(normalised["quantity"], "25")
        self.assertEqual(normalised["energyMWh"], "25")
        self.assertEqual(args["quantity"], "25")

    # Encode review and retirement content for their contract calls.
    def test_review_and_retirement_content(self) -> None:
        rejection, _ = normalise_rejection({"applicationId": "7", "reason": "Missing proof"})
        retirement, _ = normalise_retirement({"certificateId": "3", "beneficiary": "Demo", "purpose": "Electricity use"})
        self.assertEqual(json.loads(json.dumps(rejection))["applicationId"], "7")
        self.assertEqual(retirement["beneficiary"], "Demo")

    # Upload evidence and create an immutable application record through the API.
    def test_application_content_api(self) -> None:
        _, csrf = self.sign_in()
        chain = self.app.extensions["chain"]
        chain.role_name = lambda address: "Buyer"
        chain.contract_address = lambda name: "0x" + "1" * 40
        uploaded = self.client.post("/api/files", data={"file": (BytesIO(b"%PDF-1.4\ndemo"), "proof.pdf")}, headers={"X-CSRF-Token": csrf})
        self.assertEqual(uploaded.status_code, 201)
        now = int(datetime.now(timezone.utc).timestamp())
        payload = {"siteCode": "solar-01", "siteName": "Demo site", "source": "Solar", "country": "SG", "periodStart": str(now - 3600), "periodEnd": str(now - 60), "batchIndex": "1", "quantity": "25", "proofFileId": uploaded.json["data"]["fileId"]}
        response = self.client.post("/api/content", json={"kind": "application", "payload": payload}, headers={"X-CSRF-Token": csrf})
        self.assertEqual(response.status_code, 201)
        content = response.json["data"]
        self.assertEqual(content["chainArgs"]["quantity"], "25")
        self.assertEqual(content["contentHash"], "0x" + keccak(text=content["canonicalJson"]).hex())

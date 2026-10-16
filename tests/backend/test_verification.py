from __future__ import annotations

import hashlib

from eth_utils import keccak

from backend.content import canonicalise
from backend.db import open_database
from tests.backend.base import AppTestCase


class VerificationTests(AppTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.producer = "0x" + "a" * 40
        self.registry = "0x" + "b" * 40
        self.file_bytes = b"%PDF-1.4\nexample evidence"
        self.file_hash = hashlib.sha256(self.file_bytes).hexdigest()
        payload = {
            "siteCode": "SOLAR-01", "siteName": "Demo Solar Site", "source": "Solar", "country": "SG",
            "periodStart": "1790812800", "periodEnd": "1790899200", "batchIndex": "1",
            "quantity": "5", "proofSha256": self.file_hash,
        }
        envelope = {
            "schemaVersion": 1, "kind": "application", "chainId": self.app.config["CHAIN_ID"],
            "targetContract": self.registry, "creator": self.producer, "payload": payload,
        }
        canonical_json, metadata_hash = canonicalise(envelope)
        self.metadata_hash = metadata_hash
        self.application = {
            "id": "1", "status": "Approved", "certificateId": "1", "producer": self.producer,
            "quantity": "5", "metadataHash": metadata_hash,
            "siteHash": "0x" + keccak(text="SOLAR-01").hex(),
            "periodStart": payload["periodStart"], "periodEnd": payload["periodEnd"], "batchIndex": "1",
        }
        self.certificate = {
            "id": "1", "applicationId": "1", "producer": self.producer, "owner": self.producer,
            "quantity": "5", "metadataHash": metadata_hash, "status": "Active", "listed": False,
        }
        with open_database(self.app.config["DATABASE_PATH"]) as database:
            database.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             ("proof-1", self.producer, "proof.pdf", "proof-stored.pdf", self.file_hash, "application/pdf", len(self.file_bytes), 1))
            database.execute("INSERT INTO contents VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (metadata_hash, "application", self.producer, self.app.config["CHAIN_ID"], self.registry, canonical_json, 1))
            database.execute("INSERT INTO content_files VALUES (?, ?)", (metadata_hash, "proof-1"))
        (self.app.config["UPLOAD_DIR"] / "proof-stored.pdf").write_bytes(self.file_bytes)
        chain = self.app.extensions["chain"]
        chain.configured = lambda: True
        chain.contract_address = lambda name: self.registry if name == "certificateRegistry" else ""
        chain.applications = lambda: [self.application.copy()]
        chain.certificates = lambda: [self.certificate.copy()]
        chain.certificate_events = lambda certificate_id: [{
            "event": "CertificateIssued", "transactionHash": "0x" + "c" * 64,
            "blockNumber": "10", "logIndex": 0,
        }]

    def test_public_summary_and_audit_verify_hashes_without_releasing_file(self) -> None:
        response = self.client.get("/api/certificates/1/evidence-summary")
        self.assertEqual(response.status_code, 200)
        report = response.json["data"]
        self.assertEqual(report["status"], "verified")
        self.assertEqual(set(report["checks"].values()), {"passed"})
        self.assertEqual(report["summary"]["proofSha256"], self.file_hash)
        self.assertNotIn("proof-1", response.get_data(as_text=True))
        self.assertEqual(self.client.get("/api/files/proof-1").status_code, 401)
        self.app.extensions["chain"].role_name = lambda wallet: "Buyer"
        self.sign_in()
        self.assertEqual(self.client.get("/api/files/proof-1").status_code, 403)

        audit = self.client.get("/api/audit")
        self.assertEqual(audit.status_code, 200)
        self.assertEqual(audit.json["data"]["totals"]["verified"], 1)
        self.assertEqual(audit.json["data"]["events"][0]["certificateId"], "1")
        self.assertIn(b'id="auditReports"', self.client.get("/audit").data)

    def test_missing_and_changed_evidence_are_distinguished(self) -> None:
        path = self.app.config["UPLOAD_DIR"] / "proof-stored.pdf"
        path.unlink()
        missing = self.client.get("/api/certificates/1/evidence-summary").json["data"]
        self.assertEqual(missing["status"], "incomplete")
        self.assertEqual(missing["checks"]["evidenceFile"], "unavailable")

        path.write_bytes(b"%PDF-1.4\nchanged")
        changed = self.client.get("/api/certificates/1/evidence-summary").json["data"]
        self.assertEqual(changed["status"], "mismatch")
        self.assertEqual(changed["checks"]["evidenceFile"], "failed")

    def test_inconsistent_application_is_not_verified(self) -> None:
        self.application["quantity"] = "4"
        report = self.client.get("/api/certificates/1/evidence-summary").json["data"]
        self.assertEqual(report["status"], "mismatch")
        self.assertEqual(report["checks"]["approvedApplication"], "failed")

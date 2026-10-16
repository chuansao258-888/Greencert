from tests.backend.base import AppTestCase
from unittest.mock import patch
from types import SimpleNamespace
from web3 import Web3
import json

from backend.db import open_database


class PageTests(AppTestCase):
    # Pass checksum addresses to Web3 contract calls after session lookup.
    def test_wallet_summary_uses_checksum_address(self) -> None:
        address, _ = self.sign_in()
        chain = self.app.extensions["chain"]
        chain.configured = lambda: True

        def balance(wallet_address):
            self.assertTrue(Web3.is_checksum_address(wallet_address))
            self.assertEqual(wallet_address.lower(), address)
            return 123

        class Credits:
            def credits(self, wallet_address):
                self_outer.assertTrue(Web3.is_checksum_address(wallet_address))
                return self

            def call(self):
                return 0

        self_outer = self
        chain.web3 = SimpleNamespace(eth=SimpleNamespace(get_balance=balance))
        chain.contract = lambda name: SimpleNamespace(functions=Credits())
        chain.role_name = lambda wallet_address: "Buyer"
        response = self.client.get("/api/wallet")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["balanceWei"], "123")

    # Check that the public and wallet pages render.
    def test_foundation_pages_render(self) -> None:
        for path in ("/", "/dashboard", "/market", "/account", "/applications", "/my-certificates", "/activity", "/certificates/1"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"GreenCert", response.data)
        dashboard = self.client.get("/dashboard")
        self.assertIn(b'id="sourceChart"', dashboard.data)
        self.assertIn(b'id="statusChart"', dashboard.data)
        owned = self.client.get("/my-certificates")
        self.assertIn(b'aria-current="page">My RECs</a>', owned.data)
        self.assertIn(b'id="certificateArchive"', self.client.get("/market").data)

    def test_application_list_marks_missing_evidence(self) -> None:
        address, _ = self.sign_in()
        chain = self.app.extensions["chain"]
        chain.configured = lambda: True
        chain.role_name = lambda wallet_address: "Producer"
        saved_hash = "0x" + "1" * 64
        missing_hash = "0x" + "2" * 64
        chain.applications = lambda: [
            {"id": "1", "producer": address, "metadataHash": saved_hash, "status": "Approved", "quantity": "5"},
            {"id": "2", "producer": address, "metadataHash": missing_hash, "status": "Withdrawn", "quantity": "2"},
        ]
        with open_database(self.app.config["DATABASE_PATH"]) as database:
            database.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ("proof-1", address, "evidence.pdf", "stored.pdf", "sha", "application/pdf", 12, 1))
            database.execute("INSERT INTO contents VALUES (?, ?, ?, ?, ?, ?, ?)", (saved_hash, "application", address, 11155111, "0x" + "a" * 40, json.dumps({"payload": {"siteName": "Demo Solar Site"}}), 1))
            database.execute("INSERT INTO content_files VALUES (?, ?)", (saved_hash, "proof-1"))
        response = self.client.get("/api/applications")
        self.assertEqual(response.status_code, 200)
        first, second = response.json["data"]
        self.assertEqual(first["metadata"]["siteName"], "Demo Solar Site")
        self.assertEqual(first["evidenceFileId"], "proof-1")
        self.assertIsNone(second["metadata"])
        self.assertIsNone(second["evidenceFileId"])

    # Read a certificate and dashboard totals from a local chain stub.
    def test_certificate_and_dashboard_reads(self) -> None:
        chain = self.app.extensions["chain"]
        chain.configured = lambda: True
        solar_hash = "0x" + "1" * 64
        chain.certificates = lambda: [
            {"id": "1", "owner": "0x" + "a" * 40, "status": "Active", "listed": True, "quantity": "25", "metadataHash": solar_hash, "retirementHash": "0x" + "0" * 64, "listing": {"totalPriceWei": "100"}},
            {"id": "2", "owner": "0x" + "b" * 40, "status": "Retired", "listed": False, "quantity": "10", "metadataHash": "0x" + "0" * 64, "retirementHash": "0x" + "0" * 64, "listing": {"totalPriceWei": "0"}},
        ]

        class MarketStub:
            # Return a callable contract field value.
            def __init__(self):
                self.functions = self

            # Return this stub for the sold-count field.
            def soldCount(self):
                return self

            # Return this stub for the total-sales field.
            def totalSalesWei(self):
                return self

            # Return the configured count or amount.
            def call(self):
                return 0

        chain.contract = lambda name: MarketStub()
        with patch("backend.routes.api_records._content", side_effect=lambda content_hash: {"source": "Solar"} if content_hash == solar_hash else None):
            certificates = self.client.get("/api/certificates?listed=true")
            self.assertEqual(certificates.status_code, 200)
            self.assertEqual(certificates.json["data"][0]["quantity"], "25")
            dashboard = self.client.get("/api/dashboard")
        self.assertEqual(dashboard.json["data"]["listed"], 1)
        self.assertEqual(dashboard.json["data"]["issued"], 2)
        self.assertEqual(dashboard.json["data"]["active"], 1)
        self.assertEqual(dashboard.json["data"]["retired"], 1)
        self.assertEqual(dashboard.json["data"]["totalMWh"], "35")
        sources = {item["source"]: item for item in dashboard.json["data"]["sourceBreakdown"]}
        self.assertEqual(sources["Solar"]["quantityMWh"], "25")
        self.assertEqual(sources["Unknown"]["quantityMWh"], "10")
        chain.certificate_events = lambda certificate_id: [{"event": "CertificateIssued", "transactionHash": "0x" + "a" * 64, "blockNumber": "5", "logIndex": 0, "args": {"certificateId": "1"}}]
        events = self.client.get("/api/certificates/1/events")
        self.assertEqual(events.status_code, 200)
        self.assertEqual(events.json["data"][0]["event"], "CertificateIssued")

from tests.backend.base import AppTestCase
from unittest.mock import patch


class PageTests(AppTestCase):
    # Check that the public and wallet pages render.
    def test_foundation_pages_render(self) -> None:
        for path in ("/", "/dashboard", "/market", "/account", "/applications", "/my-certificates", "/activity", "/certificates/1"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"GreenCert", response.data)
        dashboard = self.client.get("/dashboard")
        self.assertIn(b'id="sourceChart"', dashboard.data)
        self.assertIn(b'id="statusChart"', dashboard.data)

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

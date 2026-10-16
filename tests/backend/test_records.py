from tests.backend.base import AppTestCase


class PageTests(AppTestCase):
    # Check that the public and wallet pages render.
    def test_foundation_pages_render(self) -> None:
        for path in ("/", "/dashboard", "/market", "/account", "/applications", "/my-certificates", "/activity"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"GreenCert", response.data)

    # Read a certificate and dashboard totals from a local chain stub.
    def test_certificate_and_dashboard_reads(self) -> None:
        chain = self.app.extensions["chain"]
        chain.configured = lambda: True
        chain.certificates = lambda: [{"id": "1", "owner": "0x" + "a" * 40, "status": "Active", "listed": True, "quantity": "25", "metadataHash": "0x" + "0" * 64, "retirementHash": "0x" + "0" * 64, "listing": {"totalPriceWei": "100"}}]

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
        certificates = self.client.get("/api/certificates?listed=true")
        self.assertEqual(certificates.status_code, 200)
        self.assertEqual(certificates.json["data"][0]["quantity"], "25")
        dashboard = self.client.get("/api/dashboard")
        self.assertEqual(dashboard.json["data"]["listed"], 1)

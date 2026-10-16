from tests.backend.base import AppTestCase


class PageTests(AppTestCase):
    def test_foundation_pages_render(self) -> None:
        for path in ("/", "/dashboard", "/market", "/account"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"GreenCert", response.data)

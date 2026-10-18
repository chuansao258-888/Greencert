from backend.routes.api_files import detect_type
from tests.backend.base import AppTestCase
from io import BytesIO


class FileTests(AppTestCase):
    # Accept supported evidence headers and reject HTML.
    def test_file_type_detection(self) -> None:
        self.assertEqual(detect_type(b"%PDF-1.4\n"), "application/pdf")
        self.assertEqual(detect_type(b"\x89PNG\r\n\x1a\nrest"), "image/png")
        self.assertEqual(detect_type(b"\xff\xd8\xffrest"), "image/jpeg")
        self.assertIsNone(detect_type(b"<html>not evidence</html>"))

    # Upload a PDF and download it with the same wallet.
    def test_evidence_upload_and_download(self) -> None:
        address, csrf = self.sign_in()
        self.app.extensions["chain"].role_name = lambda wallet: "None"
        response = self.client.post("/api/files", data={"file": (BytesIO(b"%PDF-1.4\ndemo"), "evidence.pdf")}, headers={"X-CSRF-Token": csrf})
        self.assertEqual(response.status_code, 201)
        file_id = response.json["data"]["fileId"]
        download = self.client.get(f"/api/files/{file_id}")
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.data, b"%PDF-1.4\ndemo")
        download.close()

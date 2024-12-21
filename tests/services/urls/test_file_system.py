from django.test import SimpleTestCase
from django.utils import timezone

from anchor.services.urls.file_system import FileSystemURLGenerator


class FileSystemURLGeneratorTestCase(SimpleTestCase):
    def test_url(self):
        generator = FileSystemURLGenerator()
        url = generator.url("test")
        self.assertTrue(url.startswith("/anchor/file-system"))
        self.assertFalse(url.endswith("None"))

    def test_url_with_filename(self):
        generator = FileSystemURLGenerator()
        url = generator.url("test", filename="test.txt")
        self.assertTrue(url.startswith("/anchor/file-system"))
        self.assertTrue(url.endswith("test.txt"))

    def test_url_with_mime_type(self):
        generator = FileSystemURLGenerator()
        url = generator.url("test", mime_type="image/png")
        self.assertTrue(url.startswith("/anchor/file-system"))

    def test_url_with_disposition(self):
        generator = FileSystemURLGenerator()
        url = generator.url("test", disposition="attachment")
        self.assertTrue(url.startswith("/anchor/file-system"))

    def test_url_with_expires_in(self):
        generator = FileSystemURLGenerator()
        url = generator.url("test", expires_in=timezone.timedelta(days=1))
        self.assertTrue(url.startswith("/anchor/file-system"))

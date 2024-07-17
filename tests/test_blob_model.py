import os

from django.conf import settings
from django.test import TestCase, tag

from attachments.models import Blob


class TestBlobModel(TestCase):
    GARLIC_PNG = os.path.join(settings.BASE_DIR, "fixtures", "garlic.png")

    def test_get_image_dimensions(self):
        with open(self.GARLIC_PNG, mode="rb") as f:
            b = Blob.from_file(f)
            self.assertEqual(b.file.get_dimensions(), (120, 120))

        with open(__file__, mode="rb") as f:
            b = Blob.from_file(f)
            self.assertEqual(b.file.get_dimensions(), (None, None))

    def test_from_file(self):
        with open(self.GARLIC_PNG, mode="rb") as f:
            blob = Blob.from_file(f)

            self.assertEqual(blob.filename, "garlic.png")
            self.assertEqual(blob.mime_type, "image/png")
            self.assertEqual(blob.byte_size, 8707)

            self.assertTrue(blob._state.adding)

    def test_from_path(self):
        blob = Blob.objects.from_path(self.GARLIC_PNG)
        self.assertFalse(blob._state.adding)
        self.assertGreater(blob.byte_size, 0)
        self.assertEqual(blob.filename, "garlic.png")
        self.assertEqual(blob.mime_type, "image/png")

    @tag("uses-network")
    def test_from_url(self):
        blob = Blob.objects.from_url("https://example.org/index.html")
        self.assertFalse(blob._state.adding)
        self.assertGreater(blob.byte_size, 0)
        self.assertEqual(blob.filename, "index.html")
        self.assertEqual(blob.mime_type, "text/html")

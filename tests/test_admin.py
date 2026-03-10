from django.core.files.base import ContentFile
from django.test import TestCase

from anchor.models import Attachment, Blob


class TestBlobAdminFeatures(TestCase):
    """Test the admin-related display helpers."""

    def test_attachment_count(self):
        blob = Blob.objects.create(file=ContentFile(b"test", name="test.txt"))
        Attachment.objects.create(blob=blob, content_object=blob, name="test")
        self.assertEqual(blob.attachments.count(), 1)

    def test_attachment_count_zero(self):
        blob = Blob.objects.create(file=ContentFile(b"test", name="test.txt"))
        self.assertEqual(blob.attachments.count(), 0)

    def test_blob_url_for_file_link(self):
        blob = Blob.objects.create(file=ContentFile(b"test", name="test.txt"))
        url = blob.url()
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("/"))

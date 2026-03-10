from django.core.files.base import ContentFile
from django.db.models import Count
from django.test import TestCase

from anchor.models import Attachment, Blob


class TestBlobAdminQuerySet(TestCase):
    """Test the admin-related queryset annotations and display helpers."""

    def test_attachment_count_annotation(self):
        blob = Blob.objects.create(file=ContentFile(b"test", name="test.txt"))
        Attachment.objects.create(blob=blob, content_object=blob, name="test")

        obj = Blob.objects.annotate(
            attachment_count=Count("attachments")
        ).get(pk=blob.pk)
        self.assertEqual(obj.attachment_count, 1)

    def test_attachment_count_zero(self):
        blob = Blob.objects.create(file=ContentFile(b"test", name="test.txt"))

        obj = Blob.objects.annotate(
            attachment_count=Count("attachments")
        ).get(pk=blob.pk)
        self.assertEqual(obj.attachment_count, 0)

    def test_blob_url_for_file_link(self):
        blob = Blob.objects.create(file=ContentFile(b"test", name="test.txt"))
        url = blob.url()
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("/"))

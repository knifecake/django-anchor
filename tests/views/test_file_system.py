from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse

from anchor.models import Blob


class TestFileSystemView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.blob = Blob.objects.create(file=ContentFile("test", name="test.txt"))

    def test_invalid_signed_key(self):
        response = self.client.get(
            reverse("anchor:disk", kwargs={"signed_key": "invalid"})
        )
        self.assertEqual(response.status_code, 404)

    def test_get(self):
        response = self.client.get(self.blob.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.getvalue(), b"test")

    def test_get_with_missing_file(self):
        deleted_blob = Blob.objects.create(
            file=ContentFile("deleted", name="deleted.txt")
        )
        deleted_blob.purge()
        response = self.client.get(deleted_blob.url)
        self.assertEqual(response.status_code, 404)

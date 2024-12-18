from unittest import skipUnless

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase, tag
from django.urls import reverse

from anchor.models import Blob


class TestBlobRedirectView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.blob = Blob.objects.create(file=ContentFile("test", name="test.txt"))

    def test_invalid_signed_id(self):
        response = self.client.get(
            reverse("anchor:blob_redirect", kwargs={"signed_id": "invalid"})
        )
        self.assertEqual(response.status_code, 404)

    def test_get(self):
        response = self.client.get(
            reverse("anchor:blob_redirect", kwargs={"signed_id": self.blob.signed_id})
        )
        self.assertEqual(response.status_code, 302)

    @skipUnless("r2-dev" in settings.STORAGES, "R2 is not configured")
    @tag("uses-network")
    def test_get_with_r2_blob(self):
        blob = Blob.objects.create(
            file=ContentFile("test", name="test.txt"), backend="r2-dev"
        )
        response = self.client.get(
            reverse("anchor:blob_redirect", kwargs={"signed_id": blob.signed_id})
        )
        self.assertEqual(response.status_code, 302)

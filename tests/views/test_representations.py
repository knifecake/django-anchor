from django.test import TestCase
from django.urls import reverse

from anchor.models import Blob


class TestRepresentationView(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open("tests/fixtures/garlic.png", "rb") as f:
            cls.blob = Blob.objects.create(file=f)

    def test_get(self):
        variant = self.blob.representation(
            {"format": "webp", "resize_to_fit": {"width": 20, "height": 30}}
        )
        url = reverse(
            "anchor:representation",
            kwargs={
                "signed_blob_id": self.blob.signed_id,
                "variation_key": variant.variation.key,
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        follow_response = self.client.get(url, follow=True)
        self.assertEqual(follow_response.status_code, 200)
        self.assertEqual(follow_response.get("Content-Type"), "image/webp")

    def test_invalid_key(self):
        url = reverse(
            "anchor:representation",
            kwargs={"signed_blob_id": "invalid", "variation_key": "invalid"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

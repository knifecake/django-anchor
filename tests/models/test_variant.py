from django.test import TestCase

from anchor.models import Blob, Variant


class TestVariant(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open("tests/fixtures/garlic.png", mode="rb") as file:
            cls.blob = Blob.objects.create(file=file)

    def test_key_digest(self):
        v = Variant(self.blob, {"format": "png"})
        self.assertIsInstance(v.variation_key_digest, str)

    def test_key(self):
        v = Variant(self.blob, {"format": "png"})
        self.assertTrue(v.key.startswith(f"variants/{self.blob.key}/"))

    def test_service(self):
        v = Variant(self.blob, {"format": "png"})
        self.assertEqual(type(v.service), type(self.blob.service))

    def test_url(self):
        v = Variant(self.blob, {"format": "png"})
        self.assertIsNotNone(v.url())

    def test_delete_does_not_fail_if_variant_does_not_exist(self):
        v = Variant(self.blob, {"format": "png"})
        v.delete()

    def test_process(self):
        v = Variant(self.blob, {"format": "webp", "resize_to_fit": [10, 20]})
        with v.process() as transformed:
            self.assertEqual(transformed.read(4), b"RIFF")

    def test_is_processed(self):
        v = Variant(self.blob, {"format": "webp", "resize_to_fit": [10, 20]})
        self.assertFalse(v.is_processed)

        # Processing without yielding skips processing
        v.process()
        self.assertFalse(v.is_processed)

        with v.process():
            pass
        self.assertTrue(v.is_processed)

    def test_processed(self):
        v = Variant(self.blob, {"format": "webp", "resize_to_fit": [10, 20]})
        v.delete()
        self.assertFalse(v.is_processed)
        self.assertEqual(v.processed, v)
        self.assertTrue(v.is_processed)
        self.assertTrue(v.processed.is_processed)

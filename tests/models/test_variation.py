from django.test import SimpleTestCase, override_settings

from anchor.models.variation import Variation
from anchor.services.transformers.image import ImageTransformer
from anchor.settings import anchor_settings


class TestVariation(SimpleTestCase):
    def test_wrap(self):
        v1 = Variation.wrap({"format": "png"})
        self.assertIsInstance(v1, Variation)

        v2 = Variation.wrap(v1)
        self.assertIsInstance(v2, Variation)

        v3 = Variation.wrap(Variation.encode({"format": "png"}))
        self.assertIsInstance(v3, Variation)

    def test_default_to(self):
        v = Variation({"format": "png"})
        v.default_to({"resize_to_fit": [100, 200], "format": "webp"})
        self.assertEqual(
            v.transformations, {"format": "png", "resize_to_fit": [100, 200]}
        )

    def test_encoding(self):
        transformations = {"format": "png"}
        key = Variation.encode(transformations)
        self.assertEqual(Variation.decode(key).transformations, transformations)

    def test_transformation_order_matters_for_digests(self):
        t1 = {"format": "png", "resize_to_fit": [100, 200]}
        d1 = Variation(t1).digest

        t2 = {"resize_to_fit": [100, 200], "format": "png"}
        d2 = Variation(t2).digest
        self.assertNotEqual(d1, d2)

    def test_digest_length(self):
        self.assertEqual(len(Variation({}).digest), 28)

    @override_settings(SECRET_KEY="test")
    def test_keys_are_stable(self):
        t1 = {"format": "png", "resize_to_fit": [100, 200]}
        k1 = Variation(t1).key
        expected_k1 = "eyJwIjoidmFyaWF0aW9uIiwidiI6eyJmb3JtYXQiOiJwbmciLCJyZXNpemVfdG9fZml0IjpbMTAwLDIwMF19fQ==:rlPBOdfZeqYpWMQWduoIX2Yc6vMwtksb8geBSajKuG4"

        self.assertEqual(k1, expected_k1)

    def test_transformation_order_matters_for_keys(self):
        t1 = {"format": "png", "resize_to_fit": [100, 200]}
        k1 = Variation(t1).key

        t2 = {"resize_to_fit": [100, 200], "format": "png"}
        k2 = Variation(t2).key

        self.assertNotEqual(k1, k2)

    def test_transformer(self):
        v = Variation({})
        self.assertIsInstance(v.transformer, ImageTransformer)

    def test_transform(self):
        v = Variation({"format": "webp"})
        with (
            open("tests/fixtures/garlic.png", mode="rb") as original,
            v.transform(original) as transformed,
        ):
            magic_number = transformed.read(4)
            self.assertEqual(magic_number, b"RIFF")

    def test_mime_type(self):
        v = Variation({"format": "webp"})
        self.assertEqual(v.mime_type, "image/webp")

    def test_mime_type_with_invalid_format(self):
        v = Variation({"format": "invalid"})
        self.assertEqual(v.mime_type, anchor_settings.DEFAULT_MIME_TYPE)

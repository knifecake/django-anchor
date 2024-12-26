from django.test import SimpleTestCase

from anchor.models import Blob
from anchor.models.blob.representations import NotRepresentableError


class TestRepresentations(SimpleTestCase):
    def test_is_variable(self):
        image = Blob(mime_type="image/png")
        self.assertTrue(image.is_variable)

        text = Blob(mime_type="text/plain")
        self.assertFalse(text.is_variable)

    def test_is_representable(self):
        image = Blob(mime_type="image/png")
        self.assertTrue(image.is_representable)

        text = Blob(mime_type="text/plain")
        self.assertFalse(text.is_representable)

    def test_variant(self):
        image = Blob(mime_type="image/png")
        variant = image.variant({"format": "png"})
        self.assertEqual(variant.blob, image)
        self.assertEqual(variant.variation.transformations, {"format": "png"})

    def test_representation(self):
        image = Blob(mime_type="image/png")
        representation = image.representation({"format": "png"})
        self.assertEqual(representation.blob, image)
        self.assertEqual(representation.variation.transformations, {"format": "png"})

    def test_default_variant_transformations(self):
        image = Blob(mime_type="image/png")
        self.assertEqual(
            image.variant({}).variation.transformations,
            image.default_variant_transformations,
        )

    def test_cannot_transform_non_variable_blob(self):
        text = Blob(mime_type="text/plain")
        with self.assertRaises(ValueError):
            text.variant({"format": "png"})

    def test_cannot_represent_non_variable_blob(self):
        text = Blob(mime_type="text/plain")
        with self.assertRaises(NotRepresentableError):
            text.representation({"format": "png"})

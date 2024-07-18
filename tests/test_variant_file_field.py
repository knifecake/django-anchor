import os

from django.conf import settings
from django.test import TestCase
from django.test.testcases import SimpleTestCase

from anchor.models import Blob
from anchor.models.fields import VariantFieldFile


class TestVariantFieldFile(SimpleTestCase):
    def test_guess_mime_type(self):
        self.assertEqual(VariantFieldFile.guess_mime_type("image.jpeg"), "image/jpeg")
        self.assertEqual(VariantFieldFile.guess_mime_type("image.jpg"), "image/jpeg")
        self.assertEqual(
            VariantFieldFile.guess_mime_type("image.myformat"),
            "application/octet-stream",
        )


class TestVariantFileField(TestCase):
    IMAGE_FILE = os.path.join(settings.BASE_DIR, "fixtures", "garlic.png")

    def test_file_usage(self):
        instance = Blob()
        instance.file.save("name.png", open(self.IMAGE_FILE, mode="rb"))

    def test_get_image_variant(self):
        instance = Blob()
        instance.file.save("name.png", open(self.IMAGE_FILE, mode="rb"))

        variant = instance.file.get_variant(format="webp", blocking=True)
        variant2 = instance.file.get_variant(format="webp", blocking=True)
        self.assertEqual(variant.name, variant2.name)

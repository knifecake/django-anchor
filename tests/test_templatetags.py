from django.test import TestCase
from django.conf import settings
import os
from attachments.models.blob import Blob
from attachments.templatetags.attachments import blob as blob_tag
from attachments.templatetags.attachments import blob_thumbnail as blob_thumbnail_tag


class TestBlobTag(TestCase):
    def setUp(self):
        self.raster_blob = Blob.objects.from_path(
            os.path.join(settings.BASE_DIR, "fixtures", "garlic.png")
        )

    def test_blob_tag(self):
        self.assertEqual(blob_tag(self.raster_blob), self.raster_blob.file.url)

    def test_non_blocking_blob_thumbnail_tag(self):
        """
        The non-blocking variant of the blob_thumbnail tag should return the URL
        of the original file since the variant is not ready yet. The expected
        URL should be prefixed with the URL of the original file.
        """
        self.assertIn(
            blob_tag(self.raster_blob, format="webp", blocking=False),
            self.raster_blob.file.get_variant_url(format="webp", blocking=False),
        )

    def test_blob_tag_returns_empty_string_for_none(self):
        self.assertEqual(blob_tag(None), "")

    def test_blob_tag_returns_empty_string_for_invalid_input(self):
        self.assertEqual(blob_tag("invalid input"), "")

    def test_blob_tag_works_with_variant_field_file(self):
        self.assertEqual(blob_tag(self.raster_blob.file), self.raster_blob.file.url)


class TestBlobThumbnailTag(TestCase):
    def setUp(self):
        self.raster_blob = Blob.objects.from_path(
            os.path.join(settings.BASE_DIR, "fixtures", "garlic.png")
        )
        self.vector_blob = Blob.objects.from_path(
            os.path.join(settings.BASE_DIR, "fixtures", "garlic.svg")
        )

    def test_blob_thumbnail_tag(self):
        self.assertEqual(
            blob_thumbnail_tag(
                self.raster_blob, max_width=100, max_height=100, blocking=True
            ),
            self.raster_blob.file.get_variant_url(
                thumbnail=(100, 100), format="webp", blocking=True
            ),
        )

    def test_blob_thumbnail_tag_returns_empty_string_for_none(self):
        self.assertEqual(blob_thumbnail_tag(None), "")

    def test_blob_thumbnail_tag_returns_empty_string_for_invalid_input(self):
        self.assertEqual(blob_thumbnail_tag("invalid input"), "")

    def test_blob_thumbnail_ignores_vectors(self):
        self.assertTrue(self.vector_blob.file.is_vector)
        self.assertEqual(
            blob_thumbnail_tag(self.vector_blob, ignore_vectors=True),
            self.vector_blob.file.url,
        )

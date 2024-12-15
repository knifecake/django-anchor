import base64
import os
from io import BytesIO
from unittest import skipUnless

import requests
from django.conf import settings
from django.core.files import File
from django.test import SimpleTestCase, TestCase

from anchor.models import Blob

GARLIC_PNG = os.path.join(settings.BASE_DIR, "fixtures", "garlic.png")


class TestBlobSigning(TestCase):
    def test_signing(self):
        blob = Blob.objects.create(filename="test.png")
        signed_id = blob.signed_id
        self.assertEqual(blob, Blob.objects.get_signed(signed_id))


class TestBlobUnfurling(SimpleTestCase):
    def setUp(self):
        self.blob = Blob()
        with open(GARLIC_PNG, mode="rb") as f:
            self.blob.unfurl(File(f))

    def test_filename_is_extracted(self):
        self.assertEqual(self.blob.filename, "garlic.png")

    def test_filename_is_not_extracted_if_not_available(self):
        blob = Blob(filename=None)
        blob.unfurl(File(BytesIO(b"test")))
        self.assertEqual(blob.filename, None)

    def test_filename_is_sanitized(self):
        blob = Blob()
        blob.unfurl(File(BytesIO(b"test"), name="hello world.txt"))
        self.assertEqual(blob.filename, "hello_world.txt")

        blob.unfurl(File(BytesIO(b"test"), name="John's file.txt"))
        self.assertEqual(blob.filename, "Johns_file.txt")

    def test_mime_type_is_extracted(self):
        self.assertEqual(self.blob.mime_type, "image/png")

    def test_mime_type_is_guessed_if_filename_is_not_available(self):
        blob = Blob(filename=None)
        blob.unfurl(File(BytesIO(b"test")))
        self.assertEqual(blob.mime_type, "application/octet-stream")

    def test_byte_size_is_extracted(self):
        self.assertEqual(self.blob.byte_size, 8707)

    def test_checksum_is_extracted(self):
        hex_sum = "bbbe32bf3967a22cc4ea0b885f6139ab"
        b64_sum = base64.urlsafe_b64encode(bytes.fromhex(hex_sum)).decode("utf-8")
        self.assertEqual(self.blob.checksum, b64_sum)


class TestBlobKeys(SimpleTestCase):
    def test_prefix_with_no_prefix(self):
        blob = Blob()
        self.assertEqual(blob.prefix, "")

    def test_prefix_can_be_set(self):
        blob = Blob()
        blob.prefix = "test"
        self.assertEqual(blob.prefix, "test")
        self.assertTrue(blob.key.startswith("test/"))
        self.assertTrue(len(blob.key) > len(blob.prefix))

    def test_prefix_can_be_set_multiple_times(self):
        blob = Blob()
        blob.prefix = "test"
        blob.prefix = "test2"
        self.assertEqual(blob.prefix, "test2")

    def test_prefix_can_be_set_to_none(self):
        blob = Blob()
        blob.prefix = "test"
        blob.prefix = None
        self.assertEqual(blob.prefix, "")

    def test_key_is_generated(self):
        blob = Blob()
        self.assertIsNotNone(blob.key)
        self.assertNotEqual(blob.key, "")

    def test_key_can_be_set(self):
        blob = Blob(key="test")
        self.assertEqual(blob.key, "test")

    def test_key_and_prefix_can_be_set(self):
        blob = Blob(key="test", prefix="test2")
        self.assertEqual(blob.key, "test2/test")


class TestBlobUploads(SimpleTestCase):
    def test_upload_file(self):
        blob = Blob()
        blob.upload(File(BytesIO(b"test"), name="text.txt"))

    def test_upload_file_with_prefix(self):
        blob = Blob(prefix="test")
        blob.upload(File(BytesIO(b"test"), name="text.txt"))
        self.assertTrue(blob.key.startswith("test/"))

    @skipUnless("r2-dev" in settings.STORAGES, "R2 is not configured")
    def test_upload_file_to_r2(self):
        blob = Blob(backend="r2-dev")
        blob.upload(File(BytesIO(b"test"), name="text.txt"))
        self.assertTrue(blob.key.endswith(".txt"))

    @skipUnless("r2-dev" in settings.STORAGES, "R2 is not configured")
    def test_upload_image_to_r2(self):
        blob = Blob(backend="r2-dev", prefix="test", key="image.png")
        with open(GARLIC_PNG, mode="rb") as f:
            blob.upload(File(f, name="image.png"))
        self.assertTrue(blob.key.startswith("test/"))


class TestBlobURLs(SimpleTestCase):
    def test_urls_are_generated(self):
        blob = Blob()
        self.assertIsNotNone(blob.url)
        print(blob.url)

    @skipUnless("r2-dev" in settings.STORAGES, "R2 is not configured")
    def test_urls_are_generated_for_r2(self):
        blob = Blob(backend="r2-dev", key="image.png")
        with open(GARLIC_PNG, mode="rb") as f:
            blob.upload(File(f, name="image.png"))

        url = blob.url
        self.assertIsNotNone(url)
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)

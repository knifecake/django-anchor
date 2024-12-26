import base64
import os
from io import BytesIO
from unittest import skipUnless

import requests
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from anchor.models import Attachment, Blob
from anchor.settings import anchor_settings

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

    def test_unknown_extensions_return_default_mime_type(self):
        blob = Blob()
        blob.unfurl(File(BytesIO(b"test"), name="test.unknown"))
        self.assertEqual(blob.mime_type, anchor_settings.DEFAULT_MIME_TYPE)

    def test_byte_size_is_extracted(self):
        self.assertEqual(self.blob.byte_size, 8707)

    def test_checksum_is_extracted(self):
        hex_sum = "bbbe32bf3967a22cc4ea0b885f6139ab"
        b64_sum = base64.urlsafe_b64encode(bytes.fromhex(hex_sum)).decode("utf-8")
        self.assertEqual(self.blob.checksum, b64_sum)

    def test_checksum_is_extracted_from_text_files(self):
        blob = Blob()
        blob.unfurl(ContentFile("test"))
        self.assertEqual(blob.checksum, "CY9rzUYh03PK3k6DJie09g==")

    def test_non_django_file_is_unfurled(self):
        blob = Blob()
        blob.unfurl(BytesIO(b"test"))
        self.assertIsNone(blob.filename)
        self.assertEqual(blob.mime_type, anchor_settings.DEFAULT_MIME_TYPE)
        self.assertEqual(blob.byte_size, 4)
        self.assertIsNotNone(blob.checksum)

    def test_is_image(self):
        text = Blob()
        text.upload(ContentFile(b"test", name="test.txt"))
        self.assertFalse(text.is_image)

        image = self.blob
        self.assertTrue(image.is_image)


class TestBlobKeys(SimpleTestCase):
    def test_key_is_generated(self):
        blob = Blob()
        self.assertIsNotNone(blob.key)
        self.assertNotEqual(blob.key, "")

    def test_key_can_be_set(self):
        blob = Blob(key="test")
        self.assertEqual(blob.key, "test")

    def test_str(self):
        blob = Blob(key="test")
        self.assertEqual(str(blob), blob.pk)


class TestBlobsBehaveLikeFiles(SimpleTestCase):
    def test_upload_file(self):
        blob = Blob()
        blob.upload(File(BytesIO(b"test"), name="text.txt"))

    @skipUnless("r2-dev" in settings.STORAGES, "R2 is not configured")
    def test_upload_file_to_r2(self):
        blob = Blob(backend="r2-dev")
        blob.upload(File(BytesIO(b"test"), name="text.txt"))
        self.assertIsNotNone(blob.key)
        self.assertTrue(blob.storage.exists(blob.key))

    def test_open(self):
        blob = Blob()
        blob.upload(ContentFile(b"test", name="test.txt"))
        with blob.open() as f:
            self.assertEqual(f.read(), b"test")

    def test_purge(self):
        blob = Blob()
        blob.upload(ContentFile(b"test", name="test.txt"))
        blob.purge()
        self.assertFalse(blob.storage.exists(blob.key))


class TestBlobURLs(SimpleTestCase):
    def test_urls_are_generated(self):
        blob = Blob()
        self.assertIsNotNone(blob.url)

    @skipUnless("r2-dev" in settings.STORAGES, "R2 is not configured")
    def test_urls_are_generated_for_r2(self):
        blob = Blob(backend="r2-dev", key="image.png")
        with open(GARLIC_PNG, mode="rb") as f:
            blob.upload(File(f, name="image.png"))

        url = blob.url()
        self.assertIsNotNone(url)
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)


class TestBlobQuerySet(TestCase):
    def test_get_signed(self):
        blob = Blob.objects.create(filename="test.png")
        signed_id = blob.signed_id
        self.assertEqual(blob, Blob.objects.get_signed(signed_id))

    def test_unattached_returns_all_unattached_blobs(self):
        blob = Blob.objects.create(filename="unattached_blob.png")
        attached_blob = Blob.objects.create(filename="attached_blob.png")
        Attachment.objects.create(blob=attached_blob, content_object=blob, name="test")
        self.assertEqual(blob.attachments.count(), 0)
        self.assertEqual(attached_blob.attachments.count(), 1)
        self.assertListEqual(list(Blob.objects.unattached()), [blob])

    def test_unattached_is_chainable(self):
        blob = Blob.objects.create(filename="test.png")
        old_blob = Blob.objects.create(
            filename="test2.png",
            created_at=timezone.now() - timezone.timedelta(days=10),
        )

        attached_blob = Blob.objects.create(
            filename="test3.png",
            created_at=timezone.now(),
        )
        Attachment.objects.create(blob=attached_blob, content_object=blob, name="test")
        self.assertEqual(blob.attachments.count(), 0)
        self.assertEqual(old_blob.attachments.count(), 0)
        self.assertEqual(attached_blob.attachments.count(), 1)

        self.assertListEqual(list(Blob.objects.unattached()), [blob, old_blob])

        self.assertLess(
            old_blob.created_at, timezone.now() - timezone.timedelta(days=1)
        )
        self.assertListEqual(
            list(
                Blob.objects.unattached().filter(
                    created_at__gt=timezone.now() - timezone.timedelta(days=1)
                )
            ),
            [blob],
        )

    def test_create(self):
        blob = Blob.objects.create(filename="test.png")
        self.assertIsNotNone(blob.key)
        self.assertIsNotNone(blob.created_at)

    def test_create_with_file(self):
        blob = Blob.objects.create(filename="test.png", file=ContentFile(b"test"))
        self.assertIsNotNone(blob.key)
        self.assertIsNotNone(blob.created_at)


class TestBlobCustomMetadata(SimpleTestCase):
    def test_custom_metadata_works(self):
        blob = Blob()
        blob.custom_metadata = {"test": "test"}
        self.assertEqual(blob.custom_metadata, {"test": "test"})

        blob.metadata = None
        self.assertEqual(blob.custom_metadata, dict())

        blob.custom_metadata = {"hello": "world"}
        self.assertEqual(blob.custom_metadata, {"hello": "world"})

    def test_custom_metadata_does_not_overwrite_existing_metadata(self):
        blob = Blob()
        blob.metadata = {"test": "hello"}
        blob.custom_metadata = {"test": "world"}
        self.assertEqual(blob.metadata["test"], "hello")
        self.assertEqual(blob.custom_metadata["test"], "world")

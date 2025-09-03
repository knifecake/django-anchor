import os

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.test import TestCase

from anchor.models import Attachment, Blob
from tests.dummy.models import Dummy


class TestDummy(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fixture_path = os.path.join(settings.BASE_DIR, "fixtures", "garlic.png")
        cls.dummy = Dummy.objects.create(name="Test")

    def test_new_blobs_can_be_attached(self):
        self.dummy.cover = Blob.objects.from_path(self.fixture_path)
        self.assertEqual(self.dummy.cover.filename, os.path.basename(self.fixture_path))

    def test_raw_files_can_be_attached(self):
        with open(self.fixture_path, "rb") as f:
            self.dummy.cover = f
        self.assertEqual(self.dummy.cover.filename, os.path.basename(self.fixture_path))

    def test_uploaded_files_can_be_attached(self):
        with open(self.fixture_path, "rb") as f:
            self.dummy.cover = UploadedFile(f)

        self.assertEqual(self.dummy.cover.filename, os.path.basename(self.fixture_path))

    def test_invalid_objects_cannot_be_attached(self):
        with self.assertRaises(ValueError):
            self.dummy.cover = "invalid"

    def test_cannot_attach_to_unsaved_objects(self):
        dummy = Dummy()
        with self.assertRaises(ValueError):
            dummy.cover = Blob.objects.from_path(self.fixture_path)

    def test_attachments_can_be_accessed(self):
        self.dummy.cover = Blob.objects.from_path(self.fixture_path)

        dummy = Dummy.objects.get(id=self.dummy.id)
        self.assertEqual(dummy.cover.filename, os.path.basename(self.fixture_path))

    def test_attachments_can_be_deleted(self):
        self.dummy.cover = Blob.objects.from_path(self.fixture_path)
        self.assertEqual(Attachment.objects.count(), 1)

        self.dummy.cover.delete()
        self.dummy.refresh_from_db()

        self.assertIsNone(self.dummy.cover)
        self.assertEqual(Attachment.objects.count(), 0)

    def test_setting_to_none_does_not_delete_the_attachment(self):
        self.dummy.cover = Blob.objects.from_path(self.fixture_path)
        self.assertEqual(Attachment.objects.count(), 1)

        self.dummy.cover = None
        self.dummy.refresh_from_db()
        self.assertIsNotNone(self.dummy.cover)
        self.assertEqual(Attachment.objects.count(), 1)

    def test_setting_to_false_deletes_the_attachment(self):
        self.dummy.cover = Blob.objects.from_path(self.fixture_path)
        self.assertEqual(Attachment.objects.count(), 1)

        self.dummy.cover = False
        self.dummy.refresh_from_db()
        self.assertIsNone(self.dummy.cover)
        self.assertEqual(Attachment.objects.count(), 0)

    def test_attachments_can_be_updated(self):
        self.dummy.cover = Blob.objects.from_path(self.fixture_path)
        self.assertEqual(Attachment.objects.count(), 1)
        self.assertEqual(Blob.objects.count(), 1)

        other_fixture_path = os.path.join(settings.BASE_DIR, "fixtures", "onions.jpg")
        self.dummy.cover = Blob.objects.from_path(other_fixture_path)
        self.assertEqual(Attachment.objects.count(), 1)
        self.assertEqual(Blob.objects.count(), 2)

        self.dummy.refresh_from_db()
        self.assertEqual(
            self.dummy.cover.filename, os.path.basename(other_fixture_path)
        )

    def test_attachments_can_be_copied(self):
        dummy1 = Dummy.objects.create(name="Test 1")
        dummy2 = Dummy.objects.create(name="Test 2")

        dummy1.cover = Blob.objects.from_path(self.fixture_path)
        self.assertIsNotNone(dummy1.cover)
        self.assertIsNone(dummy2.cover)
        self.assertEqual(Attachment.objects.count(), 1)
        self.assertEqual(Blob.objects.count(), 1)

        dummy2.cover = dummy1.cover
        self.assertIsNotNone(dummy2.cover)
        self.assertEqual(Attachment.objects.count(), 2)
        self.assertEqual(Blob.objects.count(), 1)

    def test_attachments_can_be_accessed_in_fresh_objects(self):
        self.dummy.cover = Blob.objects.from_path(self.fixture_path)
        self.assertIsNotNone(self.dummy.cover)
        self.assertEqual(Attachment.objects.count(), 1)
        self.assertEqual(Blob.objects.count(), 1)

        dummies = Dummy.objects.all()
        self.assertEqual(len(dummies), 1)
        self.assertIsNotNone(dummies[0].cover)
        self.assertEqual(dummies[0].cover.filename, os.path.basename(self.fixture_path))

    def test_attachments_can_be_prefetched(self):
        Dummy.objects.all().delete()
        for i in range(10):
            dummy = Dummy.objects.create(name=f"Test {i}")
            dummy.cover = Blob.objects.from_path(self.fixture_path)

        dummies = Dummy.objects.prefetch_related("cover").all()

        with self.assertNumQueries(2):
            dummies = list(dummies)
            self.assertEqual(len(dummies), 10)
            self.assertIsNotNone(dummies[0].cover)
            self.assertEqual(
                dummies[0].cover.filename, os.path.basename(self.fixture_path)
            )
            self.assertIsNotNone(dummies[1].cover)
            self.assertEqual(
                dummies[1].cover.filename, os.path.basename(self.fixture_path)
            )

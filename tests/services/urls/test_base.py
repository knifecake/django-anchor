from unittest.mock import patch

from django.core.files.storage import storages
from django.test import SimpleTestCase, override_settings

from anchor.services.urls.base import BaseURLGenerator


class BaseURLGeneratorTestCase(SimpleTestCase):
    def test_url(self):
        generator = BaseURLGenerator()
        self.assertEqual(generator.url("test"), "/test")

    def test_generators_reuse_the_configured_storage_for_each_alias(self):
        config = {
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "documents": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
                "OPTIONS": {"base_url": "/private/"},
            },
        }
        with override_settings(STORAGES=config), patch.object(
            storages, "create_storage", wraps=storages.create_storage
        ) as create:
            first = BaseURLGenerator("documents")
            second = BaseURLGenerator("documents")
            self.assertIs(first.storage, second.storage)
            self.assertIs(first.storage, storages["documents"])
            self.assertEqual(first.url("report.pdf"), "/private/report.pdf")
            self.assertEqual(create.call_count, 1)
            default = BaseURLGenerator()
            self.assertIsNot(default.storage, first.storage)
            self.assertEqual(default.url("report.pdf"), "/report.pdf")

    def test_new_generators_follow_storage_setting_changes(self):
        original = BaseURLGenerator()
        config = {
            "default": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
                "OPTIONS": {"base_url": "/replacement/"},
            }
        }
        with override_settings(STORAGES=config):
            replacement = BaseURLGenerator()
            self.assertIsNot(replacement.storage, original.storage)
            self.assertEqual(replacement.url("report.pdf"), "/replacement/report.pdf")
        restored = BaseURLGenerator()
        self.assertEqual(restored.url("report.pdf"), "/report.pdf")

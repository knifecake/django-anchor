from unittest.mock import MagicMock

from django.test import SimpleTestCase

from anchor.services.urls.s3 import S3URLGenerator


class TestS3URLGenerator(SimpleTestCase):
    def setUp(self):
        self.generator = S3URLGenerator()
        # Replace the real storage with a mock so we can inspect the call args
        # without needing a real S3/R2 backend configured.
        self.mock_storage = MagicMock()
        self.mock_storage.url.return_value = "https://example.com/file"
        self.generator.storage = self.mock_storage

    def test_url_without_disposition(self):
        self.generator.url("key")
        self.mock_storage.url.assert_called_once_with("key", expire=None, parameters={})

    def test_url_with_disposition_only(self):
        self.generator.url("key", disposition="inline")
        self.mock_storage.url.assert_called_once_with(
            "key",
            expire=None,
            parameters={"ResponseContentDisposition": "inline"},
        )

    def test_url_with_disposition_and_filename(self):
        self.generator.url("key", disposition="inline", filename="invoice.pdf")
        self.mock_storage.url.assert_called_once_with(
            "key",
            expire=None,
            parameters={"ResponseContentDisposition": 'inline; filename="invoice.pdf"'},
        )

    def test_url_with_attachment_disposition_and_filename(self):
        self.generator.url("key", disposition="attachment", filename="report.pdf")
        self.mock_storage.url.assert_called_once_with(
            "key",
            expire=None,
            parameters={
                "ResponseContentDisposition": 'attachment; filename="report.pdf"'
            },
        )

    def test_url_filename_without_disposition_is_ignored(self):
        """filename alone has no effect without a disposition value."""
        self.generator.url("key", filename="invoice.pdf")
        self.mock_storage.url.assert_called_once_with("key", expire=None, parameters={})

    def test_url_with_mime_type(self):
        self.generator.url("key", mime_type="application/pdf")
        self.mock_storage.url.assert_called_once_with(
            "key",
            expire=None,
            parameters={"ResponseContentType": "application/pdf"},
        )

    def test_url_with_mime_type_disposition_and_filename(self):
        self.generator.url(
            "key",
            mime_type="application/pdf",
            disposition="inline",
            filename="invoice.pdf",
        )
        self.mock_storage.url.assert_called_once_with(
            "key",
            expire=None,
            parameters={
                "ResponseContentType": "application/pdf",
                "ResponseContentDisposition": 'inline; filename="invoice.pdf"',
            },
        )

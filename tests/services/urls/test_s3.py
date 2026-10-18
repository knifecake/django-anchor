from datetime import timedelta
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit

from django.core.files.storage import storages
from django.test import SimpleTestCase, override_settings

from anchor.services.urls import get_for_backend
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

    def test_explicit_expiry_uses_integer_seconds_including_zero(self):
        for duration, expected in ((timedelta(hours=1), 3600), (timedelta(0), 0)):
            with self.subTest(duration=duration):
                self.mock_storage.reset_mock()
                self.generator.url("key", expires_in=duration)
                self.mock_storage.url.assert_called_once_with(
                    "key", expire=expected, parameters={}
                )
                self.assertIsInstance(
                    self.mock_storage.url.call_args.kwargs["expire"], int
                )

    def test_document_urls_reuse_the_s3_client_and_preserve_signed_parameters(self):
        config = {
            "documents": {
                "BACKEND": "storages.backends.s3.S3Storage",
                "OPTIONS": {
                    "bucket_name": "private-documents",
                    "access_key": "test-key",
                    "secret_key": "test-secret",
                    "endpoint_url": "https://storage.example.test",
                    "region_name": "us-east-1",
                    "signature_version": "s3v4",
                    "querystring_auth": True,
                    "querystring_expire": 600,
                },
            }
        }
        with override_settings(STORAGES=config):
            storage = storages["documents"]
            with patch.object(
                storage, "_create_session", wraps=storage._create_session
            ) as create_session:
                for name in ("first.pdf", "second.pdf"):
                    generator = get_for_backend("documents")
                    self.assertIs(generator.storage, storage)
                    url = generator.url(
                        name,
                        expires_in=timedelta(hours=1),
                        filename=name,
                        disposition="attachment",
                        mime_type="application/pdf",
                    )
                    link = urlsplit(url)
                    params = parse_qs(link.query)
                    self.assertIn("private-documents", link.path)
                    self.assertEqual(params["X-Amz-Expires"], ["3600"])
                    self.assertIn("X-Amz-Signature", params)
                    self.assertEqual(
                        params["response-content-type"], ["application/pdf"]
                    )
                    self.assertEqual(
                        params["response-content-disposition"],
                        [f'attachment; filename="{name}"'],
                    )
                self.assertEqual(create_session.call_count, 1)

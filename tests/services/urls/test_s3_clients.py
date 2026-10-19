import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from django.core.exceptions import SuspiciousOperation
from django.core.files.storage import storages
from django.test import SimpleTestCase, override_settings
from freezegun import freeze_time

from anchor.services.urls import get_for_backend
from anchor.services.urls import s3


def storage_config(**options):
    return {
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
                # Avoid macOS system proxy discovery in the forked offline test.
                "proxies": {},
                **options,
            },
        }
    }


@override_settings(STORAGES=storage_config())
class S3SigningClientTests(SimpleTestCase):
    def setUp(self):
        s3._reset_clients()

    def test_cold_concurrent_request_threads_share_one_client(self):
        storage = storages["documents"]
        start = Barrier(8, timeout=10)

        def sign(index):
            start.wait()
            return get_for_backend("documents").url(
                f"report-{index}.pdf",
                expires_in=timedelta(seconds=123),
                filename=f"report-{index}.pdf",
                disposition="attachment",
                mime_type="application/pdf",
            )

        with patch.object(
            storage, "_create_session", wraps=storage._create_session
        ) as create:
            with ThreadPoolExecutor(max_workers=8) as executor:
                urls = list(executor.map(sign, range(8)))
            # A second wave uses newly created request threads, as ASGI does.
            with ThreadPoolExecutor(max_workers=8) as executor:
                urls.extend(executor.map(sign, range(8)))
            self.assertEqual(create.call_count, 1)

        for index, url in enumerate(urls):
            params = parse_qs(urlsplit(url).query)
            self.assertTrue(urlsplit(url).path.endswith(f"/report-{index % 8}.pdf"))
            self.assertEqual(params["X-Amz-Expires"], ["123"])
            self.assertIn("X-Amz-Signature", params)
            self.assertEqual(params["response-content-type"], ["application/pdf"])
            self.assertEqual(
                params["response-content-disposition"],
                [f'attachment; filename="report-{index % 8}.pdf"'],
            )

    @freeze_time("2026-10-19 10:00:00")
    def test_preserves_storage_url_semantics(self):
        for signed in (True, False):
            with self.subTest(signed=signed), override_settings(
                STORAGES=storage_config(querystring_auth=signed, location="prefix")
            ):
                generator = get_for_backend("documents")
                for expiry in (None, timedelta(0), timedelta(seconds=123)):
                    expected = generator.storage.url(
                        "nested/report café +.pdf",
                        expire=None if expiry is None else int(expiry.total_seconds()),
                        parameters={
                            "ResponseContentType": "application/pdf",
                            "ResponseContentDisposition": 'attachment; filename="café.pdf"',
                        },
                    )
                    self.assertEqual(
                        generator.url(
                            "nested/report café +.pdf",
                            expires_in=expiry,
                            mime_type="application/pdf",
                            disposition="attachment",
                            filename="café.pdf",
                        ),
                        expected,
                    )
                with self.assertRaises(SuspiciousOperation):
                    generator.url("../outside.pdf")

    def test_replacement_settings_isolate_credentials_and_endpoint(self):
        first = get_for_backend("documents").url("report.pdf")
        with override_settings(
            STORAGES=storage_config(
                access_key="rotated-key",
                secret_key="rotated-secret",
                security_token="temporary-token",
                endpoint_url="https://replacement.example.test",
                bucket_name="other-bucket",
            )
        ):
            second = get_for_backend("documents").url("report.pdf")
        self.assertEqual(urlsplit(first).hostname, "storage.example.test")
        self.assertEqual(urlsplit(second).hostname, "replacement.example.test")
        self.assertIn("other-bucket", urlsplit(second).path)
        params = parse_qs(urlsplit(second).query)
        self.assertTrue(params["X-Amz-Credential"][0].startswith("rotated-key/"))
        self.assertEqual(params["X-Amz-Security-Token"], ["temporary-token"])

    def test_aliases_do_not_share_clients(self):
        config = storage_config()
        config["other"] = storage_config(
            access_key="other-key", secret_key="other-secret"
        )["documents"]
        with override_settings(STORAGES=config):
            first = get_for_backend("documents").url("report.pdf")
            second = get_for_backend("other").url("report.pdf")
        self.assertTrue(
            parse_qs(urlsplit(first).query)["X-Amz-Credential"][0].startswith(
                "test-key/"
            )
        )
        self.assertTrue(
            parse_qs(urlsplit(second).query)["X-Amz-Credential"][0].startswith(
                "other-key/"
            )
        )

    def test_custom_domain_and_cloudfront_still_delegate_to_storage(self):
        for signed in (True, False):
            signer = Mock()
            signer.generate_presigned_url.return_value = (
                "https://cdn.example.test/signed"
            )
            with self.subTest(signed=signed), override_settings(
                STORAGES=storage_config(
                    custom_domain="cdn.example.test",
                    cloudfront_signer=signer,
                    querystring_auth=signed,
                    location="prefix",
                )
            ):
                generator = get_for_backend("documents")
                with patch.object(
                    generator.storage,
                    "_create_session",
                    wraps=generator.storage._create_session,
                ) as create:
                    url = generator.url(
                        "report café.pdf",
                        disposition="attachment",
                        expires_in=timedelta(seconds=123),
                    )
                    self.assertEqual(create.call_count, 0)
                if signed:
                    self.assertEqual(url, "https://cdn.example.test/signed")
                    signer.generate_presigned_url.assert_called_once()
                else:
                    self.assertIn("cdn.example.test/prefix/report%20caf%C3%A9.pdf", url)
                    signer.generate_presigned_url.assert_not_called()

    def test_cached_client_generates_fresh_expiry_and_signature(self):
        generator = get_for_backend("documents")
        with freeze_time("2026-10-19 10:00:00"):
            first = generator.url("report.pdf", expires_in=timedelta(seconds=123))
        with freeze_time("2026-10-19 11:00:00"):
            second = generator.url("report.pdf", expires_in=timedelta(seconds=456))
        first_params, second_params = [
            parse_qs(urlsplit(url).query) for url in (first, second)
        ]
        self.assertNotEqual(first_params["X-Amz-Date"], second_params["X-Amz-Date"])
        self.assertNotEqual(
            first_params["X-Amz-Signature"], second_params["X-Amz-Signature"]
        )
        self.assertEqual(second_params["X-Amz-Expires"], ["456"])

    @skipUnless("fork" in multiprocessing.get_all_start_methods(), "Requires fork")
    def test_child_discards_inherited_client_and_locked_initialization_lock(self):
        generator = get_for_backend("documents")
        generator.url("parent.pdf")
        parent_client = s3._signing_client(generator.storage)
        context = multiprocessing.get_context("fork")
        receiver, sender = context.Pipe(duplex=False)

        def sign_in_child():
            try:
                sender.send(generator.url("child.pdf"))
            except Exception as exc:
                sender.send(f"error: {exc}")
            finally:
                sender.close()

        process = context.Process(target=sign_in_child)
        with patch.object(
            parent_client, "generate_presigned_url", return_value="inherited-client"
        ):
            try:
                # Simulate a fork while another thread is initializing a client.
                with s3._clients_lock:
                    process.start()
                sender.close()
                self.assertTrue(receiver.poll(10), "Child reused an inherited lock")
                child_url = receiver.recv()
                self.assertTrue(
                    child_url.startswith("https://storage.example.test/"), child_url
                )
                self.assertTrue(urlsplit(child_url).path.endswith("/child.pdf"))
                self.assertEqual(generator.url("parent.pdf"), "inherited-client")
                process.join(timeout=5)
                self.assertEqual(process.exitcode, 0)
            finally:
                if process.is_alive():
                    process.terminate()
                    process.join()
                receiver.close()
                sender.close()

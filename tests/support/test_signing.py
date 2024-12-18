from django.test import SimpleTestCase
from django.utils import timezone
from freezegun import freeze_time

from anchor.support.signing import AnchorSigner, ExpiredSignature, InvalidPurpose


class TestAnchorSigner(SimpleTestCase):
    def setUp(self):
        self.signer = AnchorSigner()

    def test_signing_and_unsigning(self):
        values_to_test = [
            "a simple string",
            1234,
            12.34,
            {"key": "value"},
            [1, 2, "3", "hello"],
        ]

        for value in values_to_test:
            signed = self.signer.sign(value)
            self.assertEqual(self.signer.unsign(signed), value)

    def test_signing_and_unsigning_with_purpose(self):
        signed = self.signer.sign("a simple string", purpose="test")
        self.assertEqual(self.signer.unsign(signed, purpose="test"), "a simple string")

        with self.assertRaises(InvalidPurpose):
            self.signer.unsign(signed, purpose="test2")

    def test_signing_and_unsigning_with_expires_in(self):
        signed = self.signer.sign(
            "a simple string", expires_in=timezone.timedelta(days=1)
        )
        self.assertEqual(self.signer.unsign(signed), "a simple string")

        with freeze_time(timezone.now() + timezone.timedelta(days=2)):
            with self.assertRaises(ExpiredSignature):
                self.signer.unsign(signed)

from django.test import SimpleTestCase

from anchor.support.base58 import b58encode, b58encode_int


class Base58Test(SimpleTestCase):
    def test_b58encode_int(self):
        self.assertEqual(b58encode_int(0), b"1")
        self.assertEqual(b58encode_int(0, default_one=False), b"")

    def test_b58encode(self):
        self.assertEqual(b58encode(b"hello"), b"Cn8eVZg")

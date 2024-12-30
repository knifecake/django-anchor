from django.test import SimpleTestCase

from anchor.models.base import SHORT_UUID_ALPHABET, SHORT_UUID_LENGTH, generate_pk


class TestGenShortUuid(SimpleTestCase):
    def test_gen_short_uuid(self):
        for _ in range(1000):
            self.assertEqual(len(generate_pk()), SHORT_UUID_LENGTH)
            self.assertTrue(
                all(c.encode("ascii") in SHORT_UUID_ALPHABET for c in generate_pk())
            )

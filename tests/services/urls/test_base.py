from django.test import SimpleTestCase

from anchor.services.urls.base import BaseURLGenerator


class BaseURLGeneratorTestCase(SimpleTestCase):
    def test_url(self):
        generator = BaseURLGenerator()
        self.assertEqual(generator.url("test"), "/test")

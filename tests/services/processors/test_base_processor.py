from django.test import SimpleTestCase

from anchor.services.processors.base import BaseProcessor


class TestBaseProcessor(SimpleTestCase):
    def test_source(self):
        processor = BaseProcessor()
        with self.assertRaises(NotImplementedError):
            processor.source(None)

    def test_save(self):
        processor = BaseProcessor()
        with self.assertRaises(NotImplementedError):
            processor.save(None, format=None)

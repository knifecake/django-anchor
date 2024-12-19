from django.test import SimpleTestCase

from anchor.services.transformers.base import BaseTransformer


class TestBaseTransformer(SimpleTestCase):
    def test_initialization(self):
        transformer = BaseTransformer({"resize_to_fit": (100, 100)})
        self.assertEqual(transformer.transformations, {"resize_to_fit": (100, 100)})

    def test_process(self):
        transformer = BaseTransformer({"resize_to_fit": (100, 100)})
        with self.assertRaises(NotImplementedError):
            transformer.process(None, None)

from django.test import SimpleTestCase

from anchor.services.processors.base import BaseProcessor
from anchor.services.transformers.image import ImageTransformer


class DummyProcessor(BaseProcessor):
    def __init__(self):
        self.dummy_call_count = 0

    def source(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        pass

    def dummy(self, arg1, arg2=10):
        self.dummy_call_count += 1
        return self


class TestImageTransformer(SimpleTestCase):
    def setUp(self):
        self.image = open("tests/fixtures/garlic.png", mode="rb")

    def tearDown(self):
        self.image.close()

    def test_process(self):
        transformer = ImageTransformer({})
        temp = transformer.process(self.image, "png")
        temp.seek(0)
        self.assertGreater(len(temp.read()), 0)
        temp.close()

    def test_transform(self):
        transformer = ImageTransformer({})
        with transformer.transform(self.image, "png") as temp:
            self.assertGreater(len(temp.read()), 0)

    def test_missing_transformation(self):
        transformer = ImageTransformer({"missing_transform": 10})
        with self.assertRaises(ValueError):
            transformer.process(self.image, "png")

    def test_transformation_with_args(self):
        transformer = ImageTransformer(
            {"dummy": (1, 2)}, processor_class=DummyProcessor
        )
        transformer.process(self.image, "png")
        self.assertEqual(transformer.processor.dummy_call_count, 1)

    def test_transformation_with_kwargs(self):
        transformer = ImageTransformer(
            {"dummy": {"arg1": 1, "arg2": 2}}, processor_class=DummyProcessor
        )
        transformer.process(self.image, "png")
        self.assertEqual(transformer.processor.dummy_call_count, 1)

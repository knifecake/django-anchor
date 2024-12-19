from django.test import SimpleTestCase

from anchor.services.transformers.image import ImageTransformer


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

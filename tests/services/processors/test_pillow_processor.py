import io

from django.test import SimpleTestCase
from PIL import Image

from anchor.services.processors.pillow import PillowProcessor


class TestPillowProcessor(SimpleTestCase):
    def setUp(self):
        self.image = open("tests/fixtures/garlic.png", mode="rb")

    def tearDown(self):
        self.image.close()

    def test_source(self):
        processor = PillowProcessor()
        processor.source(self.image)

    def test_save(self):
        processor = PillowProcessor()
        processor.source(self.image)

        buff = io.BytesIO()
        processor.save(buff, format="png")
        self.assertGreater(buff.getbuffer().nbytes, 0)

    def test_resize_to_fit(self):
        processor = PillowProcessor()
        processor.source(self.image)
        processor.resize_to_fit(20, 30)

        buff = io.BytesIO()
        processor.save(buff, format="png")

        self.assertLessEqual(Image.open(buff).size, (20, 30))

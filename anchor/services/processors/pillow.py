from PIL import Image

from .base import BaseProcessor


class PillowProcessor(BaseProcessor):
    def source(self, file):
        self.source = Image.open(file)
        return self

    def resize_to_fit(self, width: int, height: int):
        self.source.thumbnail((width, height))
        return self

    def save(self, file, format: str):
        self.source.save(file, format=format)
        return self

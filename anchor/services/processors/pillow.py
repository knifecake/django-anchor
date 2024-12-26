from PIL import Image

from .base import BaseProcessor


class PillowProcessor(BaseProcessor):
    """
    A file processor that uses the `Pillow <https://pypi.org/project/pillow/>`_
    library to transform images.

    To use this processor, make sure to install the Pillow library: ``pip
    install Pillow``.
    """

    def source(self, file):
        self.source = Image.open(file)
        return self

    def resize_to_fit(self, width: int, height: int):
        """
        Resize the image to fit within the given width and height, preserving
        aspect ratio.

        Aspect ratio is maintained, so the final image dimensions may be smaller
        than the provided rectangle. If the image is smaller than the provided
        dimensions, it will be upscaled.
        """
        self.source.thumbnail((width, height))
        return self

    def resize_to_limit(self, width: int, height: int):
        """
        Downsize the image to fit within the given width and height, preserving
        aspect ratio.

        If the image is already smaller than the provided dimensions, nothing is
        done.
        """
        if self.source.width <= width and self.source.height <= height:
            return self

        self.source.thumbnail((width, height))
        return self

    def rotate(self, degrees: int):
        """
        Rotates the image by the given angle.
        """
        self.source.rotate(degrees)
        return self

    def save(self, file, format: str):
        self.source.save(file, format=format)
        return self

from PIL import Image

from anchor.models.fields import VariantFieldFile


class BaseTransformer:
    def __init__(self, **format_params):
        self.format_params = format_params

        self._set_default_params()
        self._validate_format_params()

    def transform(self, src: VariantFieldFile, dst: VariantFieldFile):
        """
        Saves the transformed image to `variant_file`.
        """
        raise NotImplementedError

    def _set_default_params(self):
        """
        Assigns default parameters after initialization.
        """
        pass

    def _validate_format_params(self):
        """
        Called after self._set_default_format_params to validate their are
        consistent.

        Subclasses should override this method and raise ValueError with invalid
        parameters.
        """
        pass


class PillowImageTransformer(BaseTransformer):
    """
    Transformer for images using the Pillow package.

    Format parameters
    -----------------
    format : str or Tuple[str, Dict[str, Any]]
        Format in which to save the image. When this parameter is a tuple, the
        first argument is the format identifier, such as ``webp`` and the second
        is a dictionary of options. They are both used to call
        ``PIL.Image.save(format[0], **format[1])``. If the parameter is just a
        string, the second element of the tuple defaults to an empty dictionary
        so the Pillow defaults are used.

        See the Pillow image format documentation for more details at
        https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

    thumbnail : Tuple[int, int]
        Resizes the image to fit inside a box of the provided dimensions using
        ``PIL.Image.thumbnail``. The resized version is never larger than the
        original image.

    """

    def _set_default_params(self):
        if "format" in self.format_params:
            # if the provided format is just a string, create an empty options
            # dictionary
            if isinstance(self.format_params["format"], str):
                self.format_params["format"] = (self.format_params["format"], {})

    def transform(self, src: VariantFieldFile, dst: VariantFieldFile):
        img = Image.open(src.open())

        # create thumbnail
        thumb_size = self.format_params.get("thumbnail")
        if thumb_size is not None:
            img.thumbnail(size=thumb_size)

        # convert to another format
        if "format" in self.format_params:
            format, options = self.format_params["format"]
        else:
            format = None
            options = {}

        img.save(dst.name, format=format, **options)

        return dst

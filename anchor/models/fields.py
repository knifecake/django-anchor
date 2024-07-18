import base58
import hashlib
import mimetypes
import os
import urllib.parse
from typing import Any

from django.db import models
from django.db.models.fields.files import FieldFile, FileField
from django.utils.functional import cached_property

from anchor.tasks import blob_make_variant

DEFAULT_CONTENT_TYPE = "application/octet-stream"

# Add extra known types
mimetypes.add_type("image/jpeg", ".jfif")
mimetypes.add_type("image/webp", ".webp")


class VariantFieldFile(FieldFile):
    """
    A replacement for Django's FieldFile that works with BlobField to support
    variant generation.
    """

    def get_variant(self, blocking=False, **format_params):
        """
        Returns a variant of this file with the transformations specified by the
        keyword arguments.

        If the transformation was previously calculated, it is retrieved from
        cache.
        """

        # calculate unique name for the given parameters
        variant_name = self.get_variant_filename(**format_params)

        if self.storage.exists(variant_name):
            return self.storage.open(variant_name)

        if blocking:
            return self.make_variant(variant_name, format_params)

        blob_make_variant(self, variant_name, format_params)

    def get_variant_url(self, fallback=False, blocking=False, **format_params):
        """
        Returns the url of a variant of this file according to the params
        specified in format_params. The file is not opened if it already exists
        for efficiency. If the variant does not exist, it is created per
        `self.get_variant(**format_params)`.

        If fallback=True and the variant does not exists, the original file URL
        (which is guaranteed to be available) is returned so that the image can
        be rendered immediately.
        """
        variant_name = self.get_variant_filename(**format_params)
        try:
            if not self.storage.exists(variant_name):
                # ensure variant starts processing
                self.get_variant(blocking=blocking, **format_params)

                if blocking:
                    # if blocking the URL will be available
                    return self.storage.url(variant_name)
                elif fallback:
                    #  return a URL that is valid now if fallback is enabled
                    return self.url
                else:
                    return

        except NotImplementedError:  # pragma: no cover
            try:
                return self.url
            except ValueError:
                return None

        return self.storage.url(variant_name)

    def make_variant(self, variant_name, format_params):
        """Makes a variant synchronously."""

        # not cached, open file for writing
        variant_file = self.storage.open(variant_name, mode="wb")

        # process according to type
        if self.is_image:
            from anchor.transformers import PillowImageTransformer

            transformer = PillowImageTransformer(**format_params)
            transformer.transform(self.file, variant_file)
            return self.storage.open(variant_name)
        else:
            raise NotImplementedError(
                "Could not find transformer for mime type %s" % self.mime_type
            )

    def get_variant_filename(self, **format_params):
        """
        Names a variant for a file by appending a hash of the parameters that
        produced it.
        """

        # calculate parameter dict hash
        h1 = urllib.parse.urlencode(sorted(format_params.items()))
        h2 = hashlib.sha1(h1.encode("utf8"))

        # encode to save characters in the filename
        suffix = base58.b58encode(h2.digest()).decode()[:-1]

        # append extension to help proxy servers identify the mime type
        _, ext = os.path.splitext(self.file.name)
        format = format_params.pop("format", ext[1:])
        return f"{self.name}_{suffix}.{format}"

    def get_fingerprint(self):
        return type(self).calculate_fingerprint(self)

    def get_dimensions(self):
        """
        Returns a tuple of integers (width, height) if this file is a raster
        image. Otherwise it returns (None, None).
        """
        if not self.is_image or self.is_vector:
            return None, None

        from PIL import Image

        image = Image.open(self.open())
        return image.size

    @property
    def is_image(self):
        return self.mime_type.startswith("image")

    @property
    def is_video(self):
        return self.mime_type.startswith("video")

    @property
    def is_vector(self):
        return "svg" in self.mime_type or "pdf" in self.mime_type

    @cached_property
    def mime_type(self):
        return type(self).guess_mime_type(self.name)

    @classmethod
    def guess_mime_type(cls, filename):
        """Attempts to guess the MIME type from the extension of the filename.

        Falls back to `DEFAULT_CONTENT_TYPE` (application/octet-stream) if the
        extension is not known."""
        if filename is None:
            return DEFAULT_CONTENT_TYPE

        mime, _ = mimetypes.guess_type(filename)

        if mime is not None:
            return mime

        return DEFAULT_CONTENT_TYPE

    @classmethod
    def calculate_fingerprint(cls, file):
        m = hashlib.sha1()
        file.seek(0)
        for c in file.chunks(1024):
            m.update(c)

        return m.hexdigest()

    @property
    def filename(self):
        return os.path.basename(self.name)

    @property
    def extension(self):
        return os.path.splitext(self.name)[1]


class VariantFileField(FileField):
    """
    A replacement for Django's FileField that works with VariantFieldFiles to
    support variant generation.
    """

    attr_class = VariantFieldFile


class BlobField(models.ForeignKey):
    """
    Attach a Blob to a model.

    This field is intended to replace the default Django FileField or ImageField
    in models.
    """

    def __init__(
        self,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
        **kwargs,
    ):
        to = "anchor.Blob"

        return super().__init__(
            to=to,
            on_delete=on_delete,
            related_name=related_name,
            null=null,
            blank=blank,
            **kwargs,
        )

    def formfield(self, **kwargs: Any) -> Any:
        from anchor.forms.fields import BlobField as BlobFormField

        return super().formfield(
            **{
                "form_class": BlobFormField,
                "required": not self.blank,
                **kwargs,
            }
        )

    def deconstruct(self) -> Any:
        name, path, args, kwargs = super().deconstruct()

        # remove "to" argument from kwargs
        kwargs.pop("to", None)

        return name, path, args, kwargs

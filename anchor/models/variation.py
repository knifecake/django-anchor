import hashlib
import json
import mimetypes
from typing import Any, Self

from anchor.services.transformers.base import BaseTransformer
from anchor.services.transformers.image import ImageTransformer
from anchor.settings import anchor_settings
from anchor.support.base58 import b58encode
from anchor.support.signing import AnchorSigner


class Variation:
    """
    Represents a (set of) transformations of an image file.
    """

    PURPOSE = "variation"
    transformations: dict[str, Any]

    def __init__(self, transformations: dict[str, Any]):
        self.transformations = transformations

    @classmethod
    def wrap(cls, value: str | dict[str, Any] | Self) -> Self:
        """
        Returns a variation object, either by decoding a variation key or by
        wrapping a dictionary of transformations.

        If the argument is already a variation object, it is returned as is.
        """
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return cls.decode(value)
        else:
            return cls(value)

    def default_to(self, default_transformations: dict[str, Any]) -> None:
        """
        Updates the keys missing from this object's ``transformations`` with the
        given ``default_transformations``.
        """
        self.transformations = {**default_transformations, **self.transformations}

    @property
    def key(self) -> str:
        """
        Returns a variation key for this object.

        Keys are signed to ensure they are not tampered with, but they are
        permanent so they should be shared with care.
        """
        return type(self).encode(self.transformations)

    @property
    def digest(self) -> str:
        """
        A hash of the transformations dictionary in this variation.

        This is a good way to check if two variations are the same, but keep in
        mind that order is important in transformations, so two Variations with
        the same transformations in different orders will have different
        digests.
        """
        m = hashlib.sha1()
        m.update(json.dumps(self.transformations).encode("utf-8"))
        return b58encode(m.digest()).decode("utf-8")

    @classmethod
    def decode(cls, key: str) -> Self:
        """
        Decodes a signed variation key and returns a Variation.
        """
        transformations = cls._get_signer().unsign(key, purpose=cls.PURPOSE)
        return cls(transformations)

    @classmethod
    def encode(cls, transformations: dict[str, Any]) -> str:
        """
        Encodes a transformations dictionary as a signed string.
        """
        return cls._get_signer().sign(transformations, purpose=cls.PURPOSE)

    @classmethod
    def _get_signer(cls) -> AnchorSigner:
        return AnchorSigner()

    def transform(self, file):
        """
        Applies the transformations to the given file and makes it available as
        a temporary file in a context manager.
        """
        format = self.transformations.get("format", "png")
        return self.transformer.transform(file, format=format)

    @property
    def transformer(self) -> BaseTransformer:
        """
        Returns the transformer to be used to perform the transformations in
        this variation.
        """
        return ImageTransformer(
            {k: v for (k, v) in self.transformations.items() if k != "format"}
        )

    @property
    def mime_type(self) -> str:
        """
        Returns the MIME type that the result of applying this variation to an
        image file will have.

        It is determined from the ``format`` transformation: e.g. specifying
        ``'format': 'webp'`` will return ``'image/webp'``.
        """
        random_filename = f"random.{self.transformations['format']}"
        return (
            mimetypes.guess_type(random_filename)[0]
            or anchor_settings.DEFAULT_MIME_TYPE
        )

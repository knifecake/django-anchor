import hashlib
import json
from typing import Any, Self

from anchor.services.transformers.base import BaseTransformer
from anchor.services.transformers.image import ImageTransformer
from anchor.support.base58 import b58encode
from anchor.support.signing import AnchorSigner


class Variation:
    PURPOSE = "variation"
    transformations: dict[str, Any]

    def __init__(self, transformations: dict[str, Any]):
        self.transformations = transformations

    @classmethod
    def wrap(cls, value: str | dict[str, Any] | Self) -> Self:
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return cls.decode(value)
        else:
            return cls(value)

    @property
    def key(self) -> str:
        return type(self).encode(self.transformations)

    def digest(self) -> str:
        m = hashlib.sha1()
        m.update(json.dumps(self.transformations).encode("utf-8"))
        return b58encode(m.digest()).decode("utf-8")

    @classmethod
    def decode(cls, key: str) -> Self:
        transformations = cls._get_signer().unsign(key, purpose=cls.PURPOSE)
        return cls(transformations)

    @classmethod
    def encode(cls, transformations: dict[str, Any]) -> str:
        return cls._get_signer().sign(transformations, purpose=cls.PURPOSE)

    @classmethod
    def _get_signer(cls) -> AnchorSigner:
        return AnchorSigner()

    def transform(self, file):
        """
        Applies the transformations to the given file and makes it available as
        a temporary file in a context manager.
        """
        format = self.transformations.pop("format", "png")
        return self.transformer.transform(file, format=format)

    @property
    def transformer(self) -> BaseTransformer:
        return ImageTransformer(self.transformations)

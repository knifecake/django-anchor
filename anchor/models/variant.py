import hashlib
from contextlib import contextmanager
from typing import Any, Self

from anchor.models import Blob
from anchor.models.variation import Variation
from anchor.support.base58 import b58encode


class Variant:
    def __init__(
        self, blob: Blob, variation_or_variation_key: Variation | str | dict[str, Any]
    ):
        self.blob = blob
        self.variation = Variation.wrap(variation_or_variation_key)

    @property
    def key(self) -> str:
        return f"variants/{self.blob.key}/{self.variation_key_digest}"

    @property
    def variation_key_digest(self) -> str:
        m = hashlib.sha256()
        m.update(self.variation.key.encode("utf-8"))
        return b58encode(m.digest()).decode("utf-8")

    @property
    def service(self) -> str:
        return self.blob.service

    @property
    def url(self) -> str:
        return self.service.url(self.key)

    def delete(self) -> None:
        self.service.delete(self.key)

    @contextmanager
    def process(self):
        with (
            self.blob.open() as original,
            self.variation.transform(original) as transformed,
        ):
            self.service.save(self.key, transformed)
            transformed.seek(0)
            yield transformed

    @property
    def is_processed(self) -> bool:
        return self.service.exists(self.key)

    @property
    def processed(self) -> Self:
        if not self.is_processed:
            with self.process():
                pass
        return self

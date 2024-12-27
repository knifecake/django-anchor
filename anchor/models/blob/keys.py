import base64
import os
from secrets import token_bytes
from typing import Any, Callable

from django.db import models
from django.utils import timezone

FileLike = Any
UploadToCallable = Callable[[models.Model, FileLike], str] | str | None


class KeysMixin:
    @classmethod
    def generate_key(cls):
        """
        Generates a random key to store this blob in the storage backend.

        Keys are hard to guess, but shouldn't be shared directly with users,
        preferring to use :py:attr:`signed_id` instead, which can be expired.

        They use the base32 encoding to ensure no compatibility issues arise in
        case insensitive file systems.
        """
        return (
            base64.b32encode(token_bytes(cls.KEY_LENGTH))
            .decode("utf-8")
            .replace("=", "")
            .lower()
        )

    @classmethod
    def key_with_upload_to(
        cls,
        upload_to: UploadToCallable = None,
        instance: models.Model = None,
        file: FileLike = None,
    ) -> str:
        if upload_to is None:
            return cls.generate_key()
        elif isinstance(upload_to, str) and file is not None:
            dir = timezone.now().strftime(str(upload_to))
            return os.path.join(dir, cls.generate_key())
        elif callable(upload_to):
            return upload_to(instance, file)
        else:
            raise ValueError("upload_to must be a string or a callable")

from django.core.files.storage import storages

from .base import BaseURLGenerator
from .file_system import FileSystemURLGenerator
from .s3 import S3URLGenerator

__all__ = [
    "BaseURLGenerator",
    "FileSystemURLGenerator",
    "S3URLGenerator",
    "get_for_backend",
]


def get_for_backend(backend: str) -> BaseURLGenerator:
    """
    Given a Django storage backend name, return a ``URLGenerator`` instance that
    can work with it.

    If no suitable generator is found, this function will return the
    :py:class:`BaseURLGenerator` which delegates URL generation to the storage
    backend.
    """
    backend_config = storages.backends[backend]
    if backend_config["BACKEND"] == "django.core.files.storage.FileSystemStorage":
        return FileSystemURLGenerator(backend)
    elif backend_config["BACKEND"] == "storages.backends.s3.S3Storage":
        return S3URLGenerator(backend)
    else:
        return BaseURLGenerator(backend)

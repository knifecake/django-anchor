from django.core.files.storage import storages

from anchor.services.urls.file_system import FileSystemURLGenerator
from anchor.services.urls.s3 import S3URLGenerator

from .base import BaseURLGenerator


def get_for_backend(backend: str) -> BaseURLGenerator:
    backend_config = storages.backends[backend]
    if backend_config["BACKEND"] == "django.core.files.storage.FileSystemStorage":
        return FileSystemURLGenerator(backend)
    elif backend_config["BACKEND"] == "storages.backends.s3.S3Storage":
        return S3URLGenerator(backend)
    else:
        return BaseURLGenerator(backend)

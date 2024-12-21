from django.core.files.storage import Storage, storages
from django.utils import timezone


class BaseURLGenerator:
    backend: str
    storage: Storage

    def __init__(self, backend: str = "default"):
        self.backend = backend
        self.storage = storages.create_storage(storages.backends[self.backend])

    def url(
        self,
        key: str,
        expires_in: timezone.timedelta = None,
        mime_type: str = None,
        disposition: str = "inline",
        filename: str = None,
    ):
        return self.storage.url(key)

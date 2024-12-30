from django.core.files.storage import Storage, storages
from django.utils import timezone


class BaseURLGenerator:
    """
    Generates (signed) URLs for blobs.

    URLGenerators are a workaround against the limitations of Django's Storage
    interface, which doesn't support passing parameters for URL generation.
    These allow us to set parameters on URLs such as the content disposition
    which are necessary to ensure external backends like S3 can serve blobs
    securely.
    """

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
        """
        Generate a signed URL for the given storage key.
        """
        return self.storage.url(key)

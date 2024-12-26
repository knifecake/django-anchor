from django.urls import reverse
from django.utils import timezone

from anchor.services.urls.base import BaseURLGenerator
from anchor.settings import anchor_settings
from anchor.support.signing import AnchorSigner


class FileSystemURLGenerator(BaseURLGenerator):
    """
    Generate signed and expiring URLs for files stored in file-system storage
    backends.

    This generator exists so that we can have more control over how files stored
    via Django's default FileSystemBackend are served by making requests go
    through our file system view.
    """

    def url(
        self,
        name: str,
        expires_in: timezone.timedelta = anchor_settings.FILE_SYSTEM_BACKEND_EXPIRATION,
        filename: str = None,
        mime_type: str = None,
        disposition: str = None,
    ) -> str:
        key = self.get_key(name, mime_type=mime_type, disposition=disposition)
        signed_key = self.signer.sign(key, expires_in=expires_in, purpose="file_system")
        kwargs = {"signed_key": signed_key}
        if filename:
            kwargs["filename"] = filename
        return reverse("anchor:file_system", kwargs=kwargs)

    def get_key(self, name: str, **kwargs) -> str:
        key = {"key": name, "backend": self.backend}
        if kwargs:
            key.update(kwargs)
        return key

    @property
    def signer(self) -> AnchorSigner:
        return AnchorSigner()

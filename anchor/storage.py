from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.utils import timezone

from anchor.settings import anchor_settings
from anchor.support.signing import AnchorSigner


class AnchorFileSystemStorage(FileSystemStorage):
    def signed_url(
        self,
        name: str,
        expires_in: timezone.timedelta = anchor_settings.FILE_SYSTEM_BACKEND_EXPIRATION,
        filename: str = None,
        mime_type: str = None,
        disposition: str = None,
        backend: str = None,
    ) -> str:
        key = {"key": name}
        if mime_type:
            key["content_type"] = mime_type
        if disposition:
            key["disposition"] = disposition
        if backend:
            key["backend"] = backend

        signed_key = AnchorSigner().sign(key, expires_in=expires_in)
        return reverse(
            "anchor:disk",
            kwargs={"signed_key": signed_key, "filename": filename},
        )

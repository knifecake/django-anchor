from django.core.files.storage import FileSystemStorage
from django.urls import reverse

from anchor.models import Blob
from anchor.settings import anchor_settings


class AnchorFileSystemStorage(FileSystemStorage):
    def url(self, name: str) -> str:
        return reverse(
            "anchor:disk",
            kwargs={
                "signed_key": Blob._get_signer().sign(
                    name, expires_in=anchor_settings.FILE_SYSTEM_BACKEND_EXPIRATION
                )
            },
        )

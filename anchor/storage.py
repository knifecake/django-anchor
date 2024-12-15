from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.utils import timezone

from anchor.models.blob import Blob


class AnchorFileSystemStorage(FileSystemStorage):
    DEFAULT_EXPIRES_IN = timezone.timedelta(hours=1)

    def url(self, name: str) -> str:
        return reverse(
            "anchor:disk",
            kwargs={
                "signed_key": Blob._get_signer().sign(
                    name, expires_in=self.DEFAULT_EXPIRES_IN
                )
            },
        )

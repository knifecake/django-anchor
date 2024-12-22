import base64
import hashlib
import logging
import mimetypes
import os
from secrets import token_bytes
from typing import Any, Callable, Optional, Self

from django.core.files import File as DjangoFile
from django.core.files.storage import Storage, storages
from django.db import models
from django.utils import timezone

from anchor.models.base import BaseModel
from anchor.services.urls import get_for_backend
from anchor.settings import anchor_settings
from anchor.support.signing import AnchorSigner

from .representations import RepresentationsMixin

logger = logging.getLogger("anchor")


class BlobQuerySet(models.QuerySet):
    def get_signed(self, signed_id: str, purpose: str = None):
        key = self.model.unsign_id(signed_id, purpose)
        return self.get(key=key)

    def unattached(self):
        """
        Returns all blobs that are not attached to any model.

        Caution: the query generated by this method is expensive to compute. You
        might want to apply additional filters, for example on the blob
        `created_at` field.
        """
        return self.filter(attachments__isnull=True)

    def create(self, file: Optional[DjangoFile] = None, **kwargs):
        blob = super().create(**kwargs)
        if file:
            blob.upload(file)
        blob.save()
        return blob

    def from_path(self, path: str, **kwargs):
        with open(path, "rb") as f:
            return self.create(file=f, **kwargs)


class Blob(RepresentationsMixin, BaseModel):
    KEY_LENGTH = 30

    class Meta:
        verbose_name = "blob"
        verbose_name_plural = "blobs"

    objects = BlobQuerySet.as_manager()

    key = models.CharField(
        max_length=256, null=False, editable=False, verbose_name="key"
    )
    filename = models.CharField(
        max_length=256, verbose_name="original filename", null=True, default=None
    )
    mime_type = models.CharField(
        max_length=64,
        default=anchor_settings.DEFAULT_MIME_TYPE,
        verbose_name="MIME type",
        editable=False,
    )
    backend = models.CharField(
        max_length=64,
        default="default",
        verbose_name="backend",
        editable=False,
    )
    byte_size = models.PositiveBigIntegerField(
        verbose_name="size",
        help_text="size in bytes",
        null=True,
        blank=True,
        default=None,
        editable=False,
    )
    checksum = models.CharField(
        max_length=256,
        null=True,
        db_index=True,
        verbose_name="checksum",
        editable=False,
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name="metadata",
    )

    upload_to: str | Callable[[Self], str] | None = None

    def __init__(self, *args, upload_to=None, backend=None, **kwargs):
        super().__init__(*args, **kwargs)
        if self.key == "":
            self.key = self.generate_key()

        if backend is not None:
            self.backend = backend
        else:
            self.backend = anchor_settings.DEFAULT_STORAGE_BACKEND

        if upload_to is not None:
            self.upload_to = upload_to

            if isinstance(upload_to, str):
                self.prefix = upload_to
            elif callable(upload_to):
                self.prefix = upload_to(self)

    @property
    def signed_id(self):
        return self.get_signed_id()

    def get_signed_id(
        self,
        purpose: str = None,
        expires_in: timezone.timedelta = None,
        expires_at: timezone.datetime = None,
    ):
        return (
            type(self)
            ._get_signer()
            .sign(
                self.key, purpose=purpose, expires_in=expires_in, expires_at=expires_at
            )
        )

    @classmethod
    def unsign_id(cls, signed_id: str, purpose: str = None):
        return cls._get_signer().unsign(signed_id, purpose)

    @classmethod
    def _get_signer(cls):
        return AnchorSigner()

    @property
    def prefix(self):
        return os.path.dirname(self.key)

    @prefix.setter
    def prefix(self, value):
        if value is None:
            self.key = os.path.basename(self.key)
        else:
            self.key = os.path.join(value, os.path.basename(self.key))

    def __str__(self):
        return self.filename or self.id

    def upload(self, file: DjangoFile):
        self.unfurl(file)
        self.storage.save(self.key, file)

    def unfurl(self, file: DjangoFile | Any):
        if not isinstance(file, DjangoFile):
            file = DjangoFile(file)

        self.mime_type = self.guess_mime_type(file)
        self.byte_size = file.size
        self.checksum = self.calculate_checksum(file)
        try:
            if file.name:
                self.filename = self.storage.get_valid_name(os.path.basename(file.name))
            else:
                self.filename = None
        except TypeError:  # pragma: no cover
            self.filename = None

    def guess_mime_type(self, file: DjangoFile):
        """
        Guesses the MIME type of the given file from its name.

        If the file name is not available, returns the default MIME type.
        """
        if file.name is None:
            return anchor_settings.DEFAULT_MIME_TYPE

        mime, _ = mimetypes.guess_type(file.name)
        if mime is not None:
            return mime

        return anchor_settings.DEFAULT_MIME_TYPE

    def calculate_checksum(self, file: DjangoFile) -> str:
        """Computes the MD5 hash of the given file."""
        m = hashlib.md5()
        for c in file.chunks(chunk_size=1024):
            if isinstance(c, str):
                m.update(c.encode("utf-8"))
            else:
                m.update(c)

        return base64.urlsafe_b64encode(m.digest()).decode("utf-8")

    @property
    def storage(self) -> Storage:
        return storages.create_storage(storages.backends[self.backend])

    def generate_key(self):
        return (
            base64.b32encode(token_bytes(self.KEY_LENGTH))
            .decode("utf-8")
            .replace("=", "")
            .lower()
        )

    def url(self, expires_in: timezone.timedelta = None, disposition: str = "inline"):
        return self.url_service.url(
            self.key, expires_in=expires_in, disposition=disposition
        )

    @property
    def url_service(self):
        return get_for_backend(self.backend)

    def open(self, mode="rb"):
        return self.storage.open(self.key, mode)

    @property
    def is_image(self):
        return self.mime_type.startswith("image/")

    def purge(self):
        self.storage.delete(self.key)

    @property
    def custom_metadata(self):
        return (self.metadata or {}).get("custom", {})

    @custom_metadata.setter
    def custom_metadata(self, value):
        if self.metadata is None:
            self.metadata = dict()
        self.metadata["custom"] = value

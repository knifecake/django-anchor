import base64
import hashlib
import logging
import mimetypes
import os
from secrets import token_bytes
from typing import Optional

from django.core.files import File as DjangoFile
from django.core.files.storage import Storage, storages
from django.db import models

from anchor.models.base import BaseModel
from anchor.models.blob.signing import AnchorSigner

logger = logging.getLogger("anchor")

DEFAULT_MIME_TYPE = "application/octet-stream"


class BlobQuerySet(models.QuerySet):
    def get_signed(self, signed_id: str):
        key = self.model._get_signer().unsign(signed_id)
        return self.get(key=key)

    def unattached(self):
        return self.filter(attachments__isnull=True)

    def create(self, file: Optional[DjangoFile] = None, **kwargs):
        blob = super().create(**kwargs)
        if file:
            blob.upload(file)
        blob.save()
        return blob


class Blob(BaseModel):
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
        max_length=32,
        default=DEFAULT_MIME_TYPE,
        verbose_name="MIME type",
        editable=False,
    )
    backend = models.CharField(
        max_length=32,
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

    def __init__(self, *args, prefix=None, backend=None, **kwargs):
        super().__init__(*args, **kwargs)
        if self.key == "":
            self.key = self.generate_key()

        if prefix is not None:
            self.prefix = prefix

        if backend is not None:
            self.backend = backend

    @property
    def signed_id(self):
        return type(self)._get_signer().sign(self.key)

    def unsign_id(self, signed_id: str):
        return type(self)._get_signer().unsign(signed_id)

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
        self.service.save(self.key, file)

    def unfurl(self, file: DjangoFile):
        self.mime_type = self.guess_mime_type(file)
        self.byte_size = file.size
        self.checksum = self.calculate_checksum(file)
        try:
            if file.name:
                self.filename = self.service.get_valid_name(os.path.basename(file.name))
            else:
                self.filename = None
        except TypeError:
            pass
        extension = self.extension_with_dot
        if extension and not self.key.endswith(extension):
            self.key = f"{self.key}{extension}"

    def guess_mime_type(self, file: DjangoFile):
        """
        Guesses the MIME type of the given file from its name.

        If the file name is not available, returns the default MIME type.
        """
        if file.name is None:
            return DEFAULT_MIME_TYPE

        mime, _ = mimetypes.guess_type(file.name)
        if mime is not None:
            return mime

        return DEFAULT_MIME_TYPE

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
    def service(self) -> Storage:
        return storages.create_storage(storages.backends[self.backend])

    def generate_key(self):
        return (
            base64.b32encode(token_bytes(self.KEY_LENGTH))
            .decode("utf-8")
            .replace("=", "")
            .lower()
        )

    @property
    def extension_with_dot(self):
        if self.filename is None:
            return ""
        return os.path.splitext(self.filename)[1]

    @property
    def url(self):
        return self.service.url(self.key)

    def open(self, mode="rb"):
        return self.service.open(self.key, mode)

    @property
    def is_image(self):
        return self.mime_type.startswith("image/")

    def purge(self):
        self.service.delete(self.key)

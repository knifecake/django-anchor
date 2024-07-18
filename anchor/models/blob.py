import datetime
import logging
import os
import urllib

from django.conf import settings
from django.core.files import File as DjangoFile
from django.core.files.base import ContentFile
from django.db import models

from anchor.models.attachment import Attachment
from anchor.models.fields import (
    DEFAULT_CONTENT_TYPE,
    VariantFieldFile,
    VariantFileField,
)
from anchor.models.base import BaseModel

logger = logging.getLogger("anchor")


class BlobQuerySet(models.QuerySet):
    def create_and_attach(self, object=None, name=None, order=0, **kwargs):
        blob = super().create(**kwargs)
        Attachment.objects.create(
            blob=blob, content_object=object, order=order, name=name
        )
        return blob

    def from_url(self, url: str, **kwargs):
        """
        Downloads the file at the given URL and returns a Blob wrapping it.

        The Blob is persisted to the database but if there exists a blob with
        the same fingerprint, the existing one is reused.
        """

        with urllib.request.urlopen(url) as fp:
            contents = fp.read()
            blob = self.model.from_file(
                ContentFile(contents), filename=os.path.basename(url), **kwargs
            )
            blob.save()
            return blob

    def from_path(self, path: str, **kwargs):
        """
        Opens the file at the given ``path`` and returns a Blob wrapping it.

        The Blob is persisted to the database but if there exists a blob with
        the same fingerprint, the existing one is reused.
        """
        with open(path, mode="rb") as fp:
            blob = self.model.from_file(fp, **kwargs)
            blob.save()
            return blob


def _attachment_upload_to(instance, filename: str):
    filename = os.path.basename(filename)
    return datetime.datetime.now().strftime(
        str(f"anchor/blobs/%Y/%m/%d/{instance.pk}_{filename}")
    )


class Blob(BaseModel):
    class Meta:
        verbose_name = "blob"
        verbose_name_plural = "blobs"

    objects = BlobQuerySet.as_manager()

    file: VariantFieldFile = VariantFileField(
        upload_to=_attachment_upload_to, verbose_name="file"
    )
    alt_text = models.TextField(
        verbose_name="alternative text",
        help_text="Provide a description of the file for convenience and accessibility.",
        null=True,
        blank=True,
    )

    # automatic fields
    filename = models.CharField(
        max_length=256, verbose_name="original filename", null=True, default=None
    )
    byte_size = models.PositiveBigIntegerField(
        verbose_name="size",
        help_text="size in bytes",
        null=True,
        blank=True,
        default=None,
    )
    fingerprint = models.CharField(
        max_length=256,
        null=True,
        db_index=True,
        verbose_name="fingerprint",
        editable=False,
    )
    mime_type = models.CharField(
        max_length=32,
        default=DEFAULT_CONTENT_TYPE,
        verbose_name="MIME type",
        editable=False,
    )
    width = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="original width"
    )
    height = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="original height"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="uploaded by",
    )

    def save(self, *args, **kwargs):
        if self.filename is None:
            try:
                self.filename = os.path.basename(self.file.name)
            except TypeError:  # pragma: no cover
                pass

        if self.byte_size is None:
            self.byte_size = self.file.size

        if self.fingerprint is None:
            self.fingerprint = self.file.get_fingerprint()

        if self.mime_type is None:
            self.mime_type = self.file.mime_type

        if self.width is None and self.height is None:
            self.width, self.height = self.file.get_dimensions()

        return super().save(*args, **kwargs)

    @classmethod
    def from_file(
        cls,
        file: DjangoFile | str,
        avoid_duplicates=True,
        filename=None,
        byte_size=None,
        **kwargs,
    ):
        """
        Initializes a Blob with the given arguments, making guesses for
        arguments not provided.

        If ``avoid_duplicates`` is True and a blob exists with the same hash, it
        will be fetched, updated and returned instead of creating a new blob for
        the current file.

        By default, returned blobs are not persisted to the database. Even if
        they were already present, new attributes passed via keyword arguments
        are only updated locally. To persist changes to the database pass the
        ``save=True`` keyword argument.

        Args:
            file (DjangoFile or str): The file to wrap in a Blob.
            avoid_duplicates (bool): Whether to reuse existing blobs with the same hash.
            filename (str): The name of the file.
            byte_size (int): The size of the file in bytes.
            kwargs: Additional fields to set on the Blob.
        """
        if not isinstance(file, DjangoFile):
            file = DjangoFile(file)

        if filename is None:
            try:
                filename = os.path.basename(file.name)
            except TypeError:  # pragma: no cover
                pass

        if byte_size is None:
            byte_size = file.size

        fingerprint = VariantFieldFile.calculate_fingerprint(file)

        kwargs.update(
            {
                "fingerprint": fingerprint,
                "mime_type": VariantFieldFile.guess_mime_type(filename),
                "byte_size": byte_size,
                "filename": filename,
            }
        )
        if avoid_duplicates:
            if existing := cls.objects.filter(fingerprint=fingerprint).first():
                for k, v in kwargs.items():
                    setattr(existing, k, v)
                try:
                    existing.file.open()
                except FileNotFoundError:
                    logger.warning(
                        "Found existing blob with matching fingerprint but missing file. Replacing file with given version."
                    )
                    existing.file.save(filename, file, save=True)

                return existing

        blob = cls(**kwargs)
        blob.file.save(filename, file, save=False)
        return blob

    def __str__(self):  # pragma: no cover
        return self.file.name

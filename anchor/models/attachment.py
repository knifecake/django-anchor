from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from anchor.models.base import BaseModel


class Attachment(BaseModel):
    """
    An attachment relates your own models to Blobs.

    Most properties are proxies to the Blob.
    """

    class Meta:
        constraints = (
            models.constraints.UniqueConstraint(
                fields=("content_type", "object_id", "name", "order"),
                name="unique_attachment_per_content_type_and_object_and_name_and_order",
            ),
        )
        indexes = (
            models.Index(
                fields=("content_type", "object_id"),
                name="ix_anchor_attachment_lookups",
            ),
        )

    blob = models.ForeignKey(
        "anchor.Blob",
        on_delete=models.PROTECT,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name="blob",
    )
    """
    A reference to the Blob which stores the file for this attachment.
    """

    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.CASCADE,
        verbose_name="content type",
        db_index=False,
        related_name="+",
    )
    """
    Content Type (as in Django content types) of the object this attachment
    points to.
    """

    object_id = models.CharField(max_length=64, verbose_name="object id")
    """
    ID of the object this attachment points to.
    """

    content_object = GenericForeignKey("content_type", "object_id")
    """
    The actual object this attachment points to.
    """

    order = models.IntegerField(default=0, verbose_name="order")
    """
    The order of this attachment in the list of attachments.
    """

    name = models.CharField(max_length=256, default="attachments", verbose_name="name")
    """
    The name of this attachment.
    """

    def __str__(self) -> str:
        return str(self.blob)

    def url(self, **kwargs):
        """
        Returns a URL to the file's location in the storage backend.
        """
        return self.blob.url(**kwargs)

    @property
    def signed_id(self):
        """
        Returns a signed ID for this attachment.
        """
        return self.blob.signed_id

    @property
    def filename(self):
        """
        The filename of the file stored in the storage backend.
        """
        return self.blob.filename

    @property
    def is_image(self) -> bool:
        """
        Whether the file is an image.
        """
        return self.blob.is_image

    def representation(self, transformations: dict[str, Any]):
        """
        Returns a representation of the file. See :py:class:`the docs on
        representations
        <anchor.models.blob.representations.RepresentationsMixin>` for full
        details.
        """
        return self.blob.representation(transformations)

    def purge(self):
        """
        Deletes the file from the storage backend.
        """
        self.delete()
        self.blob.purge()

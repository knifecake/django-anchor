from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from anchor.models.base import BaseModel


class AttachmentManager(models.Manager):
    pass


class Attachment(BaseModel):
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

    objects = AttachmentManager()

    blob = models.ForeignKey(
        "anchor.Blob",
        on_delete=models.PROTECT,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name="blob",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="content type",
        db_index=False,
        related_name="+",
    )
    object_id = models.CharField(max_length=64, verbose_name="object id")
    content_object = GenericForeignKey("content_type", "object_id")

    order = models.IntegerField(default=0, verbose_name="order")
    name = models.CharField(max_length=256, default="attachments", verbose_name="name")

    def __str__(self) -> str:
        return str(self.blob)

    def url(self, **kwargs):
        return self.blob.url(**kwargs)

    @property
    def signed_id(self):
        return self.blob.signed_id

    @property
    def filename(self):
        return self.blob.filename

    @property
    def is_image(self) -> bool:
        return self.blob.is_image

    def representation(self, transformations: dict[str, Any]):
        return self.blob.representation(transformations)

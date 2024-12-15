from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from anchor.models.base import BaseModel


class Attachment(BaseModel):
    class Meta:
        constraints = (
            models.constraints.UniqueConstraint(
                fields=("content_type", "object_id", "blob", "name"),
                name="unique_attachment_per_blob_and_object_and_name",
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

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name="content type"
    )
    object_id = models.CharField(db_index=True, max_length=22, verbose_name="object id")
    content_object = GenericForeignKey("content_type", "object_id")

    order = models.IntegerField(default=0, verbose_name="order")
    name = models.CharField(max_length=256, default="attachments", verbose_name="name")

    def __str__(self) -> str:
        return f"{self.name} {self.order}"

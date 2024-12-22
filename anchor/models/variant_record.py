from django.db import models

from anchor.models.base import BaseModel
from anchor.models.fields import SingleAttachmentField


class VariantRecord(BaseModel):
    class Meta:
        verbose_name = "variant record"
        verbose_name_plural = "variant records"
        indexes = (
            models.Index(
                fields=["blob", "variation_digest"],
                name="ix_anchor_records_blob_digest",
            ),
        )

    blob = models.ForeignKey(
        "anchor.Blob",
        on_delete=models.CASCADE,
        related_name="variant_records",
        db_index=False,
        verbose_name="blob",
    )
    variation_digest = models.CharField(max_length=32, verbose_name="variation digest")
    image = SingleAttachmentField(verbose_name="image")

    def delete(self):
        self.image.delete()
        super().delete()

from django.db import models
from anchor.models.attachment import Attachment
from anchor.models.fields import BlobField


class Movie(models.Model):
    title = models.CharField(max_length=100)
    # A compulsory field that must be set on every instance
    cover = BlobField()

    # An optional file that can be left blank
    poster = BlobField(blank=True, null=True)

    @property
    def scenes(self):
        return (
            Attachment.objects.select_related("blob")
            .filter_by_object(self, name="scenes")
            .order_by("order")
            .all()
        )

    def __str__(self):
        return self.title

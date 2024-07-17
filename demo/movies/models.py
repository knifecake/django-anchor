from django.db import models
from attachments.models.fields import BlobField


class Movie(models.Model):
    title = models.CharField(max_length=100)
    cover = BlobField()
    poster = BlobField(blank=True, null=True)

    def __str__(self):
        return self.title

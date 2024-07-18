from django.db import models
from anchor.models.fields import BlobField


class Movie(models.Model):
    title = models.CharField(max_length=100)
    # A compulsory field that must be set on every instance
    cover = BlobField()

    # An optional file that can be left blank
    poster = BlobField(blank=True, null=True)

    def __str__(self):
        return self.title

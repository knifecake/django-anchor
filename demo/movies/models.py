from django.db import models

from anchor.models.fields import SingleAttachmentField


class Movie(models.Model):
    title = models.CharField(max_length=100)

    cover = SingleAttachmentField(prefix="movie-covers")

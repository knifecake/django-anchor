from django.db import models
from django.urls import reverse

from anchor.models.fields import SingleAttachmentField


class Movie(models.Model):
    title = models.CharField(max_length=100)

    cover = SingleAttachmentField(prefix="movie-covers", blank=True)

    def get_absolute_url(self):
        return reverse("movies:movie_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title

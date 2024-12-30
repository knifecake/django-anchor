from django.db import models
from django.urls import reverse

from anchor.models.fields import SingleAttachmentField


class Movie(models.Model):
    title = models.CharField(max_length=100)

    cover = SingleAttachmentField(
        upload_to="movie-covers", blank=True, help_text="A colorful image of the movie."
    )

    credits = SingleAttachmentField(
        upload_to="movie-credits",
        blank=True,
        help_text="A screenshot of the movie credits screen.",
    )

    def get_absolute_url(self):
        return reverse("movies:movie_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title

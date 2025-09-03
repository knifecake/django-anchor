from django.db import models

from anchor.models.fields import SingleAttachmentField


class Dummy(models.Model):
    name = models.CharField(max_length=255)
    cover = SingleAttachmentField()

    def __str__(self) -> str:
        return f"{self.name} - {self.cover}"

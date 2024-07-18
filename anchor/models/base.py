import uuid

import base58
from django.db import models
from django.utils.translation import gettext_lazy as _


def _gen_short_uuid():
    return base58.b58encode(uuid.uuid4().bytes).decode("ascii")


class BaseModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=22,
        verbose_name="ID",
        editable=False,
        default=_gen_short_uuid,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))

    class Meta:
        abstract = True

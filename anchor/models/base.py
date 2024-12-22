import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from anchor.support import base58

SHORT_UUID_ALPHABET: bytes = base58.BITCOIN_ALPHABET
SHORT_UUID_LENGTH = 22


def generate_pk():
    return (
        base58.b58encode(uuid.uuid4().bytes, alphabet=SHORT_UUID_ALPHABET)
        .decode("ascii")
        .ljust(SHORT_UUID_LENGTH, chr(SHORT_UUID_ALPHABET[0]))
    )


class BaseModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=SHORT_UUID_LENGTH,
        verbose_name="ID",
        editable=False,
        default=generate_pk,
    )
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name=_("created at")
    )

    class Meta:
        abstract = True

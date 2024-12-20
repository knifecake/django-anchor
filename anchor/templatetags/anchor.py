from django import template
from django.urls import reverse

from anchor.models import Attachment, Blob
from anchor.models.variant import Variant

register = template.Library()


@register.simple_tag
def blob_url(value: Blob | Attachment):
    return reverse(
        "anchor:blob",
        kwargs={"signed_id": value.signed_id, "filename": value.filename},
    )


@register.simple_tag
def variant_url(value: Variant | Blob | Attachment, **transformations):
    if isinstance(value, Variant):
        variant = value
    else:
        variant = value.representation(transformations)

    return reverse(
        "anchor:representation",
        kwargs={
            "signed_blob_id": variant.blob.signed_id,
            "variation_key": variant.variation.key,
        },
    )

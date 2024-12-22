from typing import Any

from django import template
from django.urls import reverse

from anchor.models import Attachment, Blob
from anchor.models.variant import Variant

register = template.Library()


@register.simple_tag
def blob_url(value: Blob | Attachment | None):
    if value is None:
        return ""

    return reverse(
        "anchor:blob",
        kwargs={"signed_id": value.signed_id, "filename": value.filename},
    )


@register.simple_tag
def variant_url(value: Variant | Blob | Attachment | None, **transformations):
    if value is None:
        return ""

    if isinstance(value, Variant):
        variant = value
    else:
        variant = value.representation(_preprocess_transformations(transformations))

    return reverse(
        "anchor:representation",
        kwargs={
            "signed_blob_id": variant.blob.signed_id,
            "variation_key": variant.variation.key,
        },
    )


def _preprocess_transformations(transformations: dict[str, Any]) -> dict[str, Any]:
    if "resize_to_fit" in transformations:
        width, height = transformations["resize_to_fit"].split("x")
        transformations["resize_to_fit"] = (int(width), int(height))

    return transformations

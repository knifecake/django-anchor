from django import template
from django.urls import reverse

from anchor.models import Attachment, Blob

register = template.Library()


@register.simple_tag
def blob_url(value: Blob | Attachment):
    return reverse("anchor:blob", kwargs={"signed_id": value.signed_id})

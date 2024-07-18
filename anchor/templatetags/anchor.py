import logging

from django import template

from anchor.models import Blob
from anchor.models.fields import VariantFieldFile

register = template.Library()
logger = logging.getLogger("attachments")


@register.simple_tag()
def blob(_blob: Blob | VariantFieldFile, blocking=False, **format_params):
    """
    Returns the file URL of a Blob.

    The URL returned corresponds to the original file that was uploaded as the
    blob (not any variant).

    You can also pass a VariantFieldFile instance to this tag, in which case it
    will be used instead of looking for the ``file`` attribute of a Blob. If the
    given object is neither a Blob or a VariantFieldFile, an empty string is
    returned.
    """
    if _blob is None:
        return ""

    if isinstance(_blob, Blob):
        blob_file = _blob.file
    elif isinstance(_blob, VariantFieldFile):
        blob_file = _blob
    else:
        return ""

    try:
        if format_params == {}:
            return blob_file.url
        return blob_file.get_variant_url(
            fallback=True, blocking=blocking, **format_params
        )
    except AttributeError:
        logger.exception("Error rendering blob variant.")
        return ""
    except FileNotFoundError:
        logger.error("Error opening blob variant file.")
        return ""


@register.simple_tag()
def blob_thumbnail(
    _blob: Blob | VariantFieldFile,
    max_width=1024,
    max_height=1024,
    format="webp",
    ignore_vectors=True,
    blocking=False,
    **format_params,
):
    """
    Returns the URL of a variant of the given Blob according to the specified
    format parameters.

    This tag is useful for rendering thumbnails or resized and optimized
    versions of image Blobs.
    """
    if isinstance(_blob, Blob):
        blob_file = _blob.file
    elif isinstance(_blob, VariantFieldFile):
        blob_file = _blob
    else:
        return ""

    if blob_file is None:
        return ""

    if ignore_vectors and blob_file.is_vector:
        return blob_file.url

    if blob_file.is_image:
        return blob(
            _blob,
            blocking=blocking,
            format=format,
            thumbnail=(max_width, max_height),
            **format_params,
        )

    return ""

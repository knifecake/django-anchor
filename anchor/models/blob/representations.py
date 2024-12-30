from typing import Any

from anchor.models.variation import Variation
from anchor.settings import anchor_settings


class NotRepresentableError(ValueError):
    """
    Raised when attempting to create a variant or preview which is not
    compatible with the original file.
    """

    pass


class RepresentationsMixin:
    """
    Adds methods to the :py:class:`Blob <anchor.models.blob.blob.Blob>` model to
    generate representations of files.

    Image files (those with a MIME type starting with ``image/``) can be varied
    by applying a series of transformations like resizing them or changing their
    format.

    Other kinds of files do not admit the same transformations as images, but
    can still be represented as an image, for instance, by generating a
    thumbnail of the first page of a PDF or a frame of a video.

    Previews are not yet implemented, but the :py:meth:`representation` method
    is designed to wrap both and decide internally if it should call
    :py:meth:`variant` or :py:meth:`preview` depending on the kind of file.

    If you call :py:meth:`representation` on a file that is not representable
    (e.g. trying to resize a SVG file), a :py:exc:`NotRepresentableError` will
    be raised.
    """

    def representation(self, transformations: dict[str, Any]):
        """
        Returns a :py:class:`Variant <anchor.models.variant.Variant>` or ``Preview`` object wrapping the
        result of applying the given ``transformations`` to this file.
        """
        if self.is_variable:
            return self.variant(transformations)
        elif self.is_previewable:
            return self.preview()
        else:
            raise NotRepresentableError()

    @property
    def is_representable(self) -> bool:
        """
        Checks whether the file can represented by an image or, if it is already
        an image, whether it can be transformed.
        """
        return self.is_variable or self.is_previewable

    def variant(self, transformations: dict[str, Any]):
        if not self.is_variable:
            raise ValueError("Cannot transform non-variable Blob")

        variation = Variation.wrap(transformations)
        variation.default_to(self.default_variant_transformations)
        return self.variant_class(self, variation)

    @property
    def is_variable(self) -> bool:
        return self.mime_type.startswith("image/")

    @property
    def default_variant_transformations(self) -> dict[str, Any]:
        return {"format": anchor_settings.DEFAULT_VARIANT_FORMAT}

    @property
    def variant_class(self):
        from anchor.models.variant import Variant
        from anchor.models.variant_with_record import VariantWithRecord

        if anchor_settings.TRACK_VARIANTS:
            return VariantWithRecord
        return Variant

    @property
    def is_previewable(self):
        return False

    def preview(self):
        raise NotImplementedError()

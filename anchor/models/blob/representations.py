from typing import Any

from anchor.settings import anchor_settings


class RepresentationsMixin:
    def variant(self, transformations: dict[str, Any]):
        from anchor.models.variation import Variation

        if not self.is_variable:
            raise ValueError("Cannot transform non-variable Blob")

        variation = Variation.wrap(transformations)
        variation.default_to(self.default_variant_transformations)
        return self.variant_class(self, variation)

    @property
    def is_variable(self) -> bool:
        return self.mime_type.startswith("image/")

    def representation(self, transformations: dict[str, Any]):
        if self.is_variable:
            return self.variant(transformations)

        raise ValueError("Cannot represent non-variable Blob")

    @property
    def is_representable(self) -> bool:
        return self.is_variable

    @property
    def default_variant_transformations(self) -> dict[str, Any]:
        return {"format": "webp"}

    @property
    def variant_class(self):
        from anchor.models.variant import Variant
        from anchor.models.variant_with_record import VariantWithRecord

        if anchor_settings.TRACK_VARIANTS:
            return VariantWithRecord
        return Variant

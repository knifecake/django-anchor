from contextlib import contextmanager

from django.core.files import File

from anchor.models import Blob
from anchor.models.variant import Variant
from anchor.models.variant_record import VariantRecord


class VariantWithRecord(Variant):
    @property
    def is_processed(self) -> bool:
        return self.record is not None

    def image(self):
        return self.record.image if self.record else None

    def delete(self):
        if self.record:
            self.record.delete()

        super().delete()

    @property
    def record(self) -> VariantRecord:
        return VariantRecord.objects.filter(
            blob=self.blob, variation_digest=self.variation.digest
        ).first()

    def get_or_create_record(self, image: File) -> VariantRecord:
        record = VariantRecord.objects.get_or_create(
            blob=self.blob, variation_digest=self.variation.digest
        )[0]
        image_blob = Blob.objects.create(key=self.key)
        image_blob.unfurl(image)
        image_blob.save()
        record.image = image_blob
        return record

    @contextmanager
    def process(self):
        with super().process() as image:
            self.get_or_create_record(image)
            image.seek(0)
            yield image

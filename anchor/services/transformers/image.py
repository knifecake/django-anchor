from django.utils.module_loading import import_string

from anchor.services.processors.base import BaseProcessor
from anchor.settings import anchor_settings

from .base import BaseTransformer


class ImageTransformer(BaseTransformer):
    def process(self, file, format: str):
        processor: BaseProcessor = self.get_processor()
        processor.source(file)
        for key, args in self.transformations.items():
            processor = self.apply_transformation(processor, key, args)

        temp = self._get_temporary_file(format)
        processor.save(temp, format)
        return temp

    def apply_transformation(self, processor, key, args):
        method = getattr(processor, key, None)
        if method is None:
            raise ValueError(
                f'Transformation "{key}" is not supported by the processor "{type(processor)}"'
            )

        if isinstance(args, dict):
            method(**args)
        else:
            method(*args)

        return processor

    def get_processor(self):
        processor_class = import_string(anchor_settings.IMAGE_PROCESSOR)
        return processor_class()

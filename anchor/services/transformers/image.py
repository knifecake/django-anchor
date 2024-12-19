from functools import cached_property

from django.utils.module_loading import import_string

from anchor.services.processors.base import BaseProcessor
from anchor.settings import anchor_settings

from .base import BaseTransformer


class ImageTransformer(BaseTransformer):
    def __init__(self, *args, processor_class: type[BaseProcessor] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor_class = processor_class

    def process(self, file, format: str):
        self.processor.source(file)
        for key, args in self.transformations.items():
            self.processor = self.apply_transformation(self.processor, key, args)

        temp = self._get_temporary_file(format)
        self.processor.save(temp, format)
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
        processor_class = self.processor_class or import_string(
            anchor_settings.IMAGE_PROCESSOR
        )
        return processor_class()

    @cached_property
    def processor(self):
        return self.get_processor()

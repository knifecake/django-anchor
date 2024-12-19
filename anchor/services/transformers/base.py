import tempfile
from contextlib import contextmanager
from typing import Any


class BaseTransformer:
    transformations: dict[str, Any]

    def __init__(self, transformations: dict[str, Any]):
        self.transformations = transformations

    @contextmanager
    def transform(self, file, format: str):
        """
        Applies transformation to the given file and yields a temporary file in the specified format.
        """
        output = self.process(file, format)
        try:
            output.seek(0)
            yield output
        finally:
            output.close()

    def process(self, file, format: str):
        """Returns an open temporary file with the transformed image."""
        raise NotImplementedError()

    def _get_temporary_file(self, format: str):
        return tempfile.NamedTemporaryFile(suffix=f".{format}", mode="w+b", delete=True)

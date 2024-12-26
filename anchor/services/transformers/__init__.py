"""
Transformers expose a uniform API to apply transformations to files.

They are called by :py:class:`variations <anchor.models.variation.Variation>`
and delegate actual transformations to :py:mod:`processors
<anchor.services.processors>`.
"""

from .base import BaseTransformer
from .image import ImageTransformer

__all__ = ["BaseTransformer", "ImageTransformer"]

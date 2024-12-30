"""
Processors hold the implementation details of how to transform or preview files.

They are called by :py:mod:`transformers <anchor.services.transformers>` with a
source file and are expected to produce an output after applying
transformations.

Check out the interface for processors in :py:class:`BaseProcessor` and an
implementation example in :py:class:`PillowProcessor`.
"""

from .base import BaseProcessor
from .pillow import PillowProcessor

__all__ = ["PillowProcessor", "BaseProcessor"]

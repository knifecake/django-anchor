from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.conf import settings

ANCHOR_SETTINGS_NAME = "ANCHOR"


@dataclass(frozen=True)
class AnchorSettings:
    DEFAULT_STORAGE_BACKEND: str = "default"
    """
    The default storage backend to use for Blobs when no other storage backend is specified.
    """

    DEFAULT_MIME_TYPE: str = "application/octet-stream"
    """
    The default MIME type to use for Blobs when it cannot be guessed from the file extension.
    """

    FILE_SYSTEM_BACKEND_EXPIRATION: timedelta = timedelta(hours=1)
    """
    How long URLs generated for the file system backend should be valid for.
    """

    def __getattribute__(self, name: str) -> Any:
        user_settings = getattr(settings, ANCHOR_SETTINGS_NAME, {})
        return user_settings.get(name, super().__getattribute__(name))


anchor_settings = AnchorSettings()
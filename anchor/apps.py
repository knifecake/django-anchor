import mimetypes

from django.apps import AppConfig
from django.core.checks import register

from anchor.checks import test_storage_backends


class AnchorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "anchor"
    verbose_name = "Anchor"

    def ready(self):
        register(test_storage_backends)

        # add mime type detection for webp
        if "image/webp" not in mimetypes.types_map:
            mimetypes.add_type("image/webp", ".webp", strict=True)

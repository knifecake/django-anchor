from django.core.checks import Warning


def test_storage_backends(app_configs, **kwargs):
    from django.conf import settings

    errors = []
    for name, backend in settings.STORAGES.items():
        if backend["BACKEND"] == "storages.backends.s3.S3Storage":
            if backend.get("OPTIONS", {}).get("file_overwrite", True):
                errors.append(
                    Warning(
                        "Using S3Storage with file_overwrite=True is not recommended",
                        hint=f"Set 'file_overwrite' to False in your settings.STORAGES['{name}']['OPTIONS']",
                        obj=name,
                        id="anchor.W001",
                    )
                )

    return errors

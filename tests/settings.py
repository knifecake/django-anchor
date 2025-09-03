import os

import environ

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = environ.Env()
if os.path.exists(os.path.join(BASE_DIR, "..", ".env")):
    env.read_env(os.path.join(BASE_DIR, "..", ".env"))

SECRET_KEY = "fake-key"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "tests",
    "anchor",
    "tests.dummy",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "tmp/test.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

USE_I18N = True
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
]

TIME_ZONE = "UTC"

MEDIA_ROOT = os.path.join("tmp")
STATIC_ROOT = os.path.join("tmp")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

ROOT_URLCONF = "tests.urls"

if env("R2_ENDPOINT_URL", default=None):
    STORAGES["r2-dev"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": "anchor-dev",
            "endpoint_url": env("R2_ENDPOINT_URL"),
            "access_key": env("R2_ACCESS_KEY"),
            "secret_key": env("R2_SECRET_KEY"),
            "max_memory_size": 10 * 1024 * 1024,  # 10 MB
            "querystring_auth": True,
            "querystring_expire": 600,
            "signature_version": "s3v4",
            "file_overwrite": False,
        },
    }

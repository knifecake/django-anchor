import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "fake-key"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "tests",
    "attachments",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test",
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

HUEY = {
    "immediate": True,
}

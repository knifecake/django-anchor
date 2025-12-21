# Changelog

## v0.7.0 - 2025-12-21

**Added:**

- Added explicit support for Django 6.0

**Removed:**

- Dropped support for Python <= 3.11

## v0.6.2 - 2025-09-03

**Fixed:**

- Prevent accidentally attaching files to unsaved model instances.
- Fixed single attachment related manager to work with latest Django versions
- Fixed image preview for admin widget
- Updated documentation to reference current method names
- Restored compatibility with Django 4.2

## v0.6.1 - 2025-02-09

**Fixed:**

- Fixed a bug where the mime type was not detected for webp files in some versions of Python (#11).

## v0.3.0 - 2024-07-19

**Added:**

- Added compatibility with older Django, Pillow and Python versions.

## v0.2.0 - 2024-07-18

**Added:**

- Added reference and API documentation.
- Improved package metadata

**Fixed:**

- Fixed a bug where the `anchor.admin.BlobFieldMixin` didn't have an effect on
  Blob form fields.

## v0.1.0 - 2024-07-18

Initial release.

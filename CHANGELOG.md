# Changelog

## v0.9.0 - 2026-03-11

**Improved:**

- Blob admin change view now shows a clickable link to the file that opens in a
  new tab.
- Blob admin list and detail views now show the number of attachments linked to
  each blob.
- Existing blobs are no longer editable in the admin (save buttons are hidden),
  while blob creation is still supported.

## v0.8.1 - 2026-03-10

**Fixed:**

- Fixed a bug where `Blob.__init__` silently overwrote the `backend` field with
  the default value every time a Blob was loaded from the database. This caused
  blobs stored on non-default backends (e.g. a private documents backend) to
  generate URLs using the default backend's configuration, resulting in incorrect
  hostnames and unsigned URLs.

## v0.8.0 - 2026-03-04

**Fixed:**

- `Blob.url()` now forwards the blob's `filename` to the storage backend by
  default, so browsers receive a sensible filename via the `Content-Disposition`
  header when displaying or saving files.  Pass an explicit `filename` keyword
  argument to override the default at the call site.
- `S3URLGenerator` now includes the filename in the `ResponseContentDisposition`
  parameter passed to S3-compatible backends (e.g. `inline; filename="invoice.pdf"`),
  ensuring the correct filename is suggested when files are opened in the browser
  or downloaded.
- `FileSystemView` now respects the `disposition` value encoded in the signed
  URL key, so files requested with `disposition="attachment"` are correctly
  served with `Content-Disposition: attachment` instead of always being served
  inline.
- `Blob.url()` now also forwards `mime_type` to the URL service, which allows
  S3-compatible backends to set the correct `ResponseContentType` header without
  the caller having to specify it explicitly.

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

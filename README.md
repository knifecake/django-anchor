# Django Attachments

[![Test](https://github.com/knifecake/django-attachments/actions/workflows/test.yml/badge.svg)](https://github.com/knifecake/django-attachments/actions/workflows/test.yml)

A reusable Django app to handle files attached to models, inspired by Ruby on
Rails' excellent [Active
Storage](https://edgeguides.rubyonrails.org/active_storage_overview.html).

## Features

- **Attach images and other files to your models**. Supports one or more
  individual files per model as well as multiple ordered collections of files.
- **Optimized storage.** Deduplicates files for optimized storage
- **Display files in templates.** Render resized thumbnails and optimized
  versions of your images in templates via a template tag.
- **Reduce external dependencies.** Django attachments doesn't need any external
  services and works Django's local file storage.

### Limitations

- Files are prefixed with a random string which makes the URLs for them hard to
  guess, but they are currently not protected against unauthorized attacks.
- It only works with Django storage classes in which files are accessible via
  the file system, i.e. where the
  [path](https://docs.djangoproject.com/en/5.0/ref/files/storage/#django.core.files.storage.Storage.path)
  property of a file is implemented.
- It currently depends on [Huey](https://huey.readthedocs.io/en/latest/) for
  background processing.

### Future work

- [ ] Reduce number of dependencies:
    - [ ] Make Huey dependency optional
    - [ ] Make PIL dependency optional
- [ ] Remove dependency on `base58`
- [ ] Implement private file links (maybe via signed URLs?)

## Installation

TODO

## Usage

💡 Check out the [demo](./demo/) Django project for inspiration.

### Adding files to models

The easiest way to add a file to a model is to add a `BlobField` to it:

```python
from django.db import models
from attachments.models.fields import BlobField


class Movie(models.Model):
    title = models.CharField(max_length=100)

    # A compulsory field that must be set on every instance
    cover = BlobField()

    # An optional file that can be left blank
    poster = BlobField(blank=True, null=True)
```

Notice how the `BlobField` above can be customized by setting the `blank` and
`null` options like any other field. It will also accept any other core field
parameters.

BlobFields are ForeignKey fields under the hood, so after you've added or made
changes you need to generate a migration with `python manage.py makemigrations`
and then apply it via `python manage.py migrate`.

Once your migrations are applied you can assign an
`attachments.models.blob.Blob` object to a `BlobField` much like you'd assign a
`DjangoFile` object to a `FileField`:

```python
from attachments.models.blob import Blob

# A new Blob objects is created and saved to the database with the file metadata
cover = Blob.objects.from_url('...')

# Make our movie point to that Blob object
movie.cover = cover
movie.save()
```

### Using files in templates

Django attachments comes with a handy template tag to render URLs of files you've stored:

```
{% load attachments %}
<img src="{% blob_thumbnail movie.poster max_width=300 max_height=600 format='jpeg' %}">
```

The above call to `blob_thumbnail` will generate an optimized version of the
movie's cover in JPEG format which fits inside a 300x600 rectangle. Optimized
versions are generated asynchronously and if they're not ready for immediate use
the original file's URL is returned instead to avoid blocking the request.

## Contributing

PRs and issues are very welcome!

Check out [CONTRIBUTING.md](./CONTRIBUTING.md) to learn how to set up the
project locally.

## License

This project is released under the MIT License. Check out
[LICENSE](./LICENSE.md) to get the full text of the license.

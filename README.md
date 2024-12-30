# Django Anchor

[![Test](https://github.com/knifecake/django-anchor/actions/workflows/test.yml/badge.svg)](https://github.com/knifecake/django-anchor/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/django-anchor/badge/?version=latest)](https://django-anchor.readthedocs.io/en/latest/?badge=latest)

Django Anchor is a reusable Django app that allows you to attach files to models.

Anchor works very similarly to Django's ``FileField`` and ``ImageField`` model
fields, but adds a few extra features:

- Images can be resized, converted to another format and otherwise transformed.
- Files are served through signed URLs that can expire after a configurable
  amount of time, even when using the default file-system storage backend.

Django Anchor is essentially a port of the excellent [Active
Storage](https://edgeguides.rubyonrails.org/active_storage_overview.html) Ruby
on Rails feature, but leveraging existing Django abstractions and packages of
the Python ecosystem. Some features are not yet implemented, but the core
concepts are there two eventually be able to support them.

## Installation

Check out the [installation
guide](https://django-anchor.readthedocs.io/en/latest/installation.html) in the
documentation for more details.

Django-anchor is compatible with Django >= 4.2 and Python >= 3.11.

1. Add the `django-anchor` package to your dependencies. You can do this by
   running:

       pip install django-anchor

   or by adding `django-anchor` to your `requirements.txt` or `pyproject.toml`
   files if you have one.

2. Add  `anchor` to `settings.INSTALLED_APPS`

3. Add URL configuration to your project:

   ```python
   urlpatterns = [
       path('anchor/', include('anchor.urls')),
   ]
   ```

4. Run migrations:

   ```bash
   python manage.py migrate
   ```

In addition, if you wish to create image variants, a Pillow >= 9.5 should be
available in your system.

## Usage

💡 Check out the [demo](./demo/) Django project for inspiration and the [Getting
Started
guide](https://django-anchor.readthedocs.io/en/latest/getting_started.html) in
the documentation.

### Adding files to models

The easiest way to add a file to a model is to add a `BlobField` to it:

```python
from django.db import models
from anchor.models.fields import SingleAttachmentField


class Movie(models.Model):
    title = models.CharField(max_length=100)

    cover = SingleAttachmentField()
```

That's it! No need to run ``makemigrations`` or ``migrate`` since Django Anchor
doesn't actually need any columns added to the model.

The ``cover`` field works just like any other model field:

```python
# Create a new movie
movie = Movie.objects.create(title="My Movie")

# Attach an uploaded file
movie.cover = uploaded_file

# Get a URL to the file
movie.cover.url()

# Get a URL to a miniature version of the file
movie.cover.representation(resize_to_fit=(200, 200), format="webp").url()
```

### Using files in templates

Django anchor comes with a handy template tag to render URLs of files you've stored:

```
{% load anchor %}
<img src="{% variant_url movie.cover resize_to_limit='300x600' format='jpeg' %}">
```

The above call to `variant_url` will generate an optimized version of the
movie's cover in JPEG format which fits inside a 300x600 rectangle.

## Contributing

PRs and issues are very welcome!

Check out [CONTRIBUTING.md](./CONTRIBUTING.md) to learn how to set up the
project locally.

## License

This project is released under the MIT License. Check out
[LICENSE](./LICENSE.md) to get the full text of the license.

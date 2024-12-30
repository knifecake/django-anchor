============
Installation
============

1. Add the ``django-anchor`` package to your dependencies. You can do this by
   running::

       pip install django-anchor

   or by adding ``django-anchor`` to your ``requirements.txt`` or
   ``pyproject.toml`` files if you have one.

   If you intend to transform images you'll also need to install ``Pillow``. See
   below for more details.

2. Add  ``anchor`` to ``settings.INSTALLED_APPS``

3. Add URL configuration to your project:

   .. code-block:: python

       urlpatterns = [
           path('anchor/', include('anchor.urls')),
       ]


4. Run migrations:

   .. code-block:: bash

       python manage.py migrate


By default, Anchor works with your ``default`` storage backend. If you want to use a
different storage backend, define it under ``STORAGES`` in your project settings
and set ``ANCHOR['DEFAULT_STORAGE_BACKEND']`` to the name of your preferred
storage backend.

Check out the full configuration options in :doc:`configuration </configuration>`.


Additional dependencies for image transformations
=================================================

Using Anchor to generate representations of images requires the ``Pillow``
Python package. You can add it to your dependencies, and there's no need to add
anything to the ``INSTALLED_APPS`` setting.

Keep in mind that while Pillow is a powerful library with lots of available
operations, Anchor only supports a handful of them. Check out the
:py:class:`PillowProcessor documentation
<anchor.services.processors.PillowProcessor>` for a list of supported
operations.

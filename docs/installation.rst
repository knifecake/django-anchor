============
Installation
============

1. Add the ``django-anchor`` package to your dependencies. You can do this by
   running::

       pip install django-anchor

   or by adding ``django-anchor`` to your ``requirements.txt`` or
   ``pyproject.toml`` files if you have one.

2. Add  ``anchor`` to ``settings.INSTALLED_APPS``

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

By default, anchor works with your default storage backend. If you want to use a
different storage backend, define it under ``STORAGES`` in your project settings
and set ``ANCHOR['DEFAULT_STORAGE_BACKEND']`` to the name of your preferred
storage backend.

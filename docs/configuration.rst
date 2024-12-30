=============
Configuration
=============

Django Anchor exposes several settings which can be changed to tune the
application to your needs. Define these settings under ``ANCHOR`` in your project
settings like this:

.. code-block:: python

    ANCHOR = {
        'DEFAULT_STORAGE_BACKEND': 'my_storage_backend',
    }


.. autoclass:: anchor.settings.AnchorSettings
   :members:

=============
Django Anchor
=============

Django Anchor is a reusable Django app that allows you to attach files to models.

Anchor works very similarly to Django's ``FileField`` and ``ImageField`` model
fields, but adds a few extra features:

- Images can be resized, converted to another format and otherwise transformed.
- Files are served through signed URLs that can expire after a configurable
  amount of time, even when using the default file-system storage backend.

Django Anchor is essentially a port of the excellent `Active Storage
<https://edgeguides.rubyonrails.org/active_storage_overview.html>`_ Ruby on
Rails feature, but leveraging existing Django abstractions and packages of the
Python ecosystem. Some features are not yet implemented, but the core concepts
are there two eventually be able to support them.

Table of contents
=================
.. toctree::
    getting_started
    installation
    configuration
    api/index

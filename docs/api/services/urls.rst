====
URLs
====

.. automodule:: anchor.services.urls
    :members:

S3 signing clients
==================

For the standard ``storages.backends.s3.S3Storage`` backend, Anchor reuses a
low-level S3 client across URL generators and request threads. Client creation
is serialized, clients are isolated by storage instance, and forked children
start with an empty cache and a new initialization lock. Boto3 sessions and
resources are not shared between threads by this cache.

URLs themselves are never cached: each call signs its own key, expiry and
response parameters. Replacing Django's ``STORAGES`` configuration creates new
storage instances and therefore new signing clients. Custom-domain and
CloudFront URL generation continues to use django-storages directly.

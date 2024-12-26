=============================
Models
=============================


Core models
-----------

There are two core models in Anchor:

- :py:class:`Blobs <anchor.models.blob.blob.Blob>` which take care of storing a
  pointer to each file uploaded plus some metadata, and
- :py:class:`Attachments <anchor.models.attachment.Attachment>` which act as a
  bridge between your own models and :py:class:`Blobs
  <anchor.models.blob.blob.Blob>`, allowing you to attach files to your own
  records.

These, together with the :py:class:`VariantRecord
<anchor.models.variant_record.VariantRecord>` are the only models backed by a
database table. The rest of the classes within the ``anchor.models`` module only
contain business logic.

.. autoclass:: anchor.models.blob.blob.Blob
   :members:

.. autoclass:: anchor.models.attachment.Attachment
   :members:

Fields
------

Model fields are how you allow your models to hold files.

.. autoclass:: anchor.models.fields.SingleAttachmentField


Representations
---------------

.. automodule:: anchor.models.blob.representations
   :members:

.. automodule:: anchor.models.variant
   :members:

.. automodule:: anchor.models.variant_record
   :members:

.. automodule:: anchor.models.variant_with_record
   :members:

.. automodule:: anchor.models.variation
   :members:

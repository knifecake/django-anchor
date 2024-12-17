from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import File
from django.db import models
from django.db.models import Model

from anchor.models import Attachment, Blob


class ReverseSingleAttachmentDescriptor:
    def __init__(self, name: str, prefix: str = None, backend: str = None):
        self.name = name
        self.prefix = prefix
        self.backend = backend

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        return Attachment.objects.filter(
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
            name=self.name,
            order=0,
        ).first()

    def __set__(self, instance, value):
        if isinstance(value, Attachment):
            value.object_id = instance.id
            value.content_type = ContentType.objects.get_for_model(instance)
            value.name = self.name
            value.order = 0
            value.save()

        if isinstance(value, Blob):
            blob = value
        elif isinstance(value, File):
            blob = Blob.objects.create(
                file=value, backend=self.backend, prefix=self.prefix
            )
        else:
            raise ValueError(f"Invalid value type: {type(value)}")

        Attachment.objects.update_or_create(
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
            name=self.name,
            order=0,
            defaults={"blob": blob},
        )


class SingleAttachmentField(GenericRelation):
    def __init__(self, prefix: str = None, backend: str = None, **kwargs):
        self.prefix = prefix
        self.backend = backend
        self.object_id_field_name = "object_id"
        self.content_type_field_name = "content_type"
        self.for_concrete_model = True

        # Bypass the GenericRelation constructor to be able to set editable=True
        super(GenericRelation, self).__init__(
            to="anchor.Attachment",
            related_name="+",
            related_query_name="+",
            editable=True,
            serialize=False,
            from_fields=[],
            to_fields=[],
            null=True,
            blank=True,
            rel=self.rel_class(
                self,
                to="anchor.Attachment",
                related_name="+",
                related_query_name="+",
                limit_choices_to=None,
            ),
            **kwargs,
            on_delete=models.CASCADE,
        )

    def contribute_to_class(self, cls: type[Model], name: str, **kwargs) -> None:
        super().contribute_to_class(cls, name, **kwargs)
        setattr(
            cls,
            name,
            ReverseSingleAttachmentDescriptor(
                name=name, prefix=self.prefix, backend=self.backend
            ),
        )

    def formfield(self, **kwargs):
        from django.forms import FileField

        return FileField(**kwargs)


"""
from movies.models import Movie
from django.core.files.base import ContentFile
movie = Movie.objects.first()
movie.cover = ContentFile(b'test', name='test.txt')
"""

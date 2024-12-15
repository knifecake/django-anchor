from django.contrib.contenttypes.models import ContentType
from django.core.files.base import File
from django.db.models import Model
from django.db.models.fields.related import RelatedField

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
        elif isinstance(value, Blob):
            Attachment.objects.update_or_create(
                object_id=instance.id,
                content_type=ContentType.objects.get_for_model(instance),
                name=self.name,
                order=0,
                defaults={"blob": value},
            )
        elif isinstance(value, File):
            Attachment.objects.create(
                object_id=instance.id,
                content_type=ContentType.objects.get_for_model(instance),
                blob=Blob.objects.create(
                    file=value, backend=self.backend, prefix=self.prefix
                ),
                name=self.name,
                order=0,
            )
        else:
            raise ValueError(f"Invalid value type: {type(value)}")


class SingleAttachmentField(RelatedField):
    # Field flags
    many_to_many = False
    many_to_one = False
    one_to_many = False
    one_to_one = True

    def __init__(self, prefix: str = None, backend: str = None, **kwargs):
        self.prefix = prefix
        self.backend = backend
        super().__init__(
            related_name=None,
            related_query_name=None,
            limit_choices_to=None,
            editable=False,
            serialize=False,
            **kwargs,
        )

    def resolve_related_fields(self):
        self.to_fields = [self.model._meta.pk.name]
        return [
            (
                self.remote_field.model._meta.get_field("object_id"),
                self.model._meta.pk,
            )
        ]

    def contribute_to_class(self, cls: type[Model], name: str, **kwargs) -> None:
        setattr(
            cls,
            name,
            ReverseSingleAttachmentDescriptor(
                name=name, prefix=self.prefix, backend=self.backend
            ),
        )

    def contribute_to_related_class(self, cls, related):
        pass


"""
from movies.models import Movie
from django.core.files.base import ContentFile
movie = Movie.objects.first()
movie.cover = ContentFile(b'test', name='test.txt')
"""

from typing import Any, Callable

from django.contrib.contenttypes.fields import GenericRel, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Model
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor
from django.utils.functional import cached_property
from django.utils.text import capfirst

from anchor.models import Attachment, Blob


class SingleAttachmentRel(GenericRel):
    """
    Holds information about the relation between an Attachment and the Model
    where the SingleAttachmentField is defined.
    """

    field: "SingleAttachmentField"

    def __init__(self, field: "SingleAttachmentField"):
        self.field = field
        super().__init__(
            field=field,
            to="anchor.Attachment",
            related_name="+",
            related_query_name="+",
        )

    @cached_property
    def cache_name(self):
        # Use the name given to the field in the model instance to avoid
        # collisions when there are multiple SingleAttachmentFields defined on
        # the same instance
        return self.field.attname


class ReverseSingleAttachmentDescriptor(ReverseOneToOneDescriptor):
    def __init__(
        self,
        related: GenericRel,
        name: str,
        upload_to: str | Callable[[models.Model, Any], str] = None,
        backend: str = None,
    ):
        self.related = related
        self.name = name
        self.upload_to = upload_to
        self.backend = backend

    def __get__(self, instance, cls=None) -> Attachment | None:
        try:
            return super().__get__(instance, cls=cls)
        except Attachment.DoesNotExist:
            return None

    def __set__(self, instance, value):
        # Be compatible with how Django handles files in the forms API. A
        # None value signifies that the file was not updated, while a False
        # value signifies that the file should be deleted.
        if value is None:
            return

        if value is False and self.__get__(instance, cls=Attachment):
            self.__get__(instance, cls=Attachment).delete()
            return

        if isinstance(value, Attachment):
            if value._state.adding:
                value.object_id = instance.id
                value.content_type = ContentType.objects.get_for_model(instance)
                value.name = self.name
                value.order = 0
                value.save()

            return

        if isinstance(value, Blob):
            blob = value
        elif hasattr(value, "read"):  # quacks like a file?
            blob = Blob.objects.create(
                file=value,
                backend=self.backend,
                key=Blob.key_with_upload_to(
                    upload_to=self.upload_to, file=value, instance=instance
                ),
            )
        else:
            raise ValueError(
                f"Invalid value type {type(value)}. Provide a File, a Blob or an Attachment."
            )

        Attachment.objects.update_or_create(
            **self.related.field.get_forward_related_filter(instance),
            defaults={"blob": blob},
        )

    def get_queryset(self, **hints):
        return (
            Attachment._base_manager.db_manager(hints=hints)
            .select_related("blob")
            .all()
        )

    def get_prefetch_querysets(self, instances, querysets=None):
        if querysets and len(querysets) != 1:
            raise ValueError(
                "querysets argument of get_prefetch_querysets() should have a length "
                "of 1."
            )
        queryset = querysets[0] if querysets else self.get_queryset()
        queryset._add_hints(instance=instances[0])
        queryset = queryset.filter(
            object_id__in=(instance.id for instance in instances),
            content_type=ContentType.objects.get_for_model(instances[0]),
            name=self.name,
            order=0,
        )
        rel_obj_attr = self.related.field.get_local_related_value

        def instance_attr(i):
            return tuple(
                str(x) for x in self.related.field.get_foreign_related_value(i)
            )

        instances_dict = {instance_attr(inst): inst for inst in instances}

        # Since we're going to assign directly in the cache,
        # we must manage the reverse relation cache manually.
        for rel_obj in queryset:
            instance = instances_dict[rel_obj_attr(rel_obj)]
            self.related.field.set_cached_value(rel_obj, instance)
        return (
            queryset,
            rel_obj_attr,
            instance_attr,
            True,
            self.related.cache_name,
            False,
        )


class SingleAttachmentField(GenericRelation):
    """
    Enables a model to hold a single attachment.

    When accessing this field, you'll get an :py:class:`Attachment
    <anchor.models.attachment.Attachment>` instance. To set the file attachment,
    you can assign a plain file-like object, a :py:class:`Blob
    <anchor.models.blob.blob.Blob>` instance or an :py:class:`Attachment
    <anchor.models.attachment.Attachment>` instance.

    Example:
        A SingleAttachmentField allows attaching a single file to a model
        instance:

        >>> from django.db import models
        >>> from anchor.models.fields import SingleAttachmentField
        >>>
        >>> class Movie(models.Model):
        ...     title = models.CharField(max_length=100)
        ...     cover = SingleAttachmentField(
        ...         upload_to="movie-covers",
        ...         help_text="A colorful image of the movie."
        ...     )
        ...
        >>> movie = Movie.objects.create(title="The Matrix")
        >>> movie.cover = uploaded_file  # Attach a file
        >>> movie.cover.url()  # Get URL to original file
        '/media/movie-covers/matrix-cover.jpg'
    """

    rel_class = SingleAttachmentRel

    def __init__(
        self,
        upload_to: str | Callable[[models.Model, Blob], str] = None,
        backend: str = None,
        **kwargs,
    ):
        self.upload_to = upload_to
        self.backend = backend
        self.object_id_field_name = "object_id"
        self.content_type_field_name = "content_type"
        self.for_concrete_model = True

        kwargs["null"] = True
        kwargs["related_name"] = "+"
        kwargs["related_query_name"] = "+"
        kwargs["on_delete"] = models.CASCADE
        kwargs["to_fields"] = []
        kwargs["from_fields"] = []
        kwargs["serialize"] = False

        self.rel = self.rel_class(field=self)

        # Bypass the GenericRelation constructor to be able to set editable=True
        super(GenericRelation, self).__init__(
            to="anchor.Attachment",
            rel=self.rel,
            **kwargs,
        )

    def contribute_to_class(self, cls: type[Model], name: str, **kwargs) -> None:
        super().contribute_to_class(cls, name, **kwargs)
        setattr(
            cls,
            name,
            ReverseSingleAttachmentDescriptor(
                related=self.rel,
                name=name,
                upload_to=self.upload_to,
                backend=self.backend,
            ),
        )

    def formfield(self, **kwargs):
        from anchor.forms.fields import SingleAttachmentField

        super().formfield(**kwargs)
        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
        }
        defaults.update(kwargs)

        return SingleAttachmentField(**defaults)

    def get_forward_related_filter(self, obj):
        return {
            "object_id": obj.id,
            "content_type": ContentType.objects.get_for_model(obj),
            "name": self.name,
            "order": 0,
        }

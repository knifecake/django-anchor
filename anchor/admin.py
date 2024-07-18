from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from anchor.models.fields import BlobField
from anchor.forms.widgets import AdminBlobInput
from anchor.models.attachment import Attachment
from anchor.models.blob import Blob
from django.template.defaultfilters import filesizeformat


class BlobFieldMixin:
    """
    Render a preview of the blob in the admin form.

    Inherit from this in your ModelAdmin class to render a preview of the blob
    in the admin form.
    """

    formfield_overrides = {
        BlobField: {"widget": AdminBlobInput},
    }


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("blob", "name", "content_type", "content_object")
    raw_id_fields = ("blob",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("blob", "content_type")
            .prefetch_related("content_object")
        )


@admin.register(Blob)
class BlobAdmin(BlobFieldMixin, admin.ModelAdmin):
    ordering = ("id",)
    date_hierarchy = "created_at"
    search_fields = ("filename", "id", "fingerprint", "uploaded_by__email")
    list_display = ("filename", "human_size", "uploaded_by", "created_at")
    list_filter = ("mime_type",)
    readonly_fields = ("filename", "byte_size", "fingerprint", "thumbnail")
    raw_id_fields = ("uploaded_by",)

    def save_model(self, request, obj, form, change):  # pragma: no cover
        if not change:
            obj.uploaded_by = request.user

        super().save_model(request, obj, form, change)

    @admin.display(description="Size", ordering="byte_size")
    def human_size(self, instance: Blob):
        return filesizeformat(instance.byte_size)

    def thumbnail(self, instance: Blob):
        if instance.file and instance.file.is_image:
            return format_html(
                '<img src="{}" style="max-width: 100%">', instance.file.url
            )

        return "-"


class AttachmentInline(GenericTabularInline):
    """
    Inline for Attachment model.

    Add this to the admin.ModelAdmin.inlines attribute of the model you want to attach files to.
    """

    model = Attachment
    extra = 0
    fields = ("blob", "name", "order", "thumbnail")
    readonly_fields = ("thumbnail",)
    ordering = ("name", "order")
    autocomplete_fields = ("blob",)

    def thumbnail(self, instance):
        if instance.blob:
            return format_html(
                '<img src="{}" style="max-width: 100%">', instance.blob.file.url
            )

        return "-"

    thumbnail.short_description = "Thumbnail"

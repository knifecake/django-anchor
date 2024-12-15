from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.template.defaultfilters import filesizeformat
from django.utils.html import format_html

from anchor.models.attachment import Attachment
from anchor.models.blob import Blob


class AdminBlobForm(forms.ModelForm):
    class Meta:
        model = Blob
        fields = []

    backend = forms.ChoiceField(
        choices=[(k, k) for k in settings.STORAGES.keys()], initial="default"
    )
    file = forms.FileField()
    prefix = forms.CharField(required=False)

    def save(self, commit=True):
        blob = Blob(
            prefix=self.cleaned_data["prefix"], backend=self.cleaned_data["backend"]
        )

        blob.upload(self.cleaned_data["file"])
        blob.save()
        return blob

    def save_m2m(self):
        pass


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
class BlobAdmin(admin.ModelAdmin):
    ordering = ("id",)
    date_hierarchy = "created_at"
    search_fields = ("filename", "id", "checksum")
    list_display = ("filename", "human_size", "backend", "created_at")
    list_filter = ("backend", "mime_type")
    readonly_fields = (
        "filename",
        "mime_type",
        "byte_size",
        "checksum",
        "preview",
        "key",
    )

    @admin.display(description="Size", ordering="byte_size")
    def human_size(self, instance: Blob):
        return filesizeformat(instance.byte_size)

    def preview(self, instance: Blob):
        if instance.is_image and instance.url:
            return format_html('<img src="{}" style="max-width: 100%">', instance.url)

        return "-"

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return AdminBlobForm

        return super().get_form(request, obj, **kwargs)


class AttachmentInline(GenericTabularInline):
    """
    Inline for Attachment model.

    Add this to the admin.ModelAdmin.inlines attribute of the model you want to attach files to.
    """

    model = Attachment
    extra = 0
    fields = ("blob", "name", "order", "preview")
    readonly_fields = ("preview",)
    ordering = ("name", "order")
    autocomplete_fields = ("blob",)

    def preview(self, instance):
        if instance.blob:
            return format_html(
                '<img src="{}" style="max-width: 100%">', instance.blob.file.url
            )

        return "-"

    preview.short_description = "preview"

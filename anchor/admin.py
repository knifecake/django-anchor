import os
from typing import Any

from django import forms
from django.conf import settings
from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.html import format_html

from anchor.models import Attachment, Blob, VariantRecord
from anchor.settings import anchor_settings


class AdminBlobForm(forms.ModelForm):
    class Meta:
        model = Blob
        fields = []

    backend = forms.ChoiceField(
        choices=[
            (k, k)
            for k, v in settings.STORAGES.items()
            if v["BACKEND"] != "django.contrib.staticfiles.storage.StaticFilesStorage"
        ],
        initial=anchor_settings.DEFAULT_STORAGE_BACKEND,
    )
    file = forms.FileField()

    def save(self, commit=True):
        return Blob.objects.create(
            file=self.cleaned_data["file"],
            backend=self.cleaned_data["backend"],
            key=self.get_key(self.cleaned_data["file"]),
        )

    def save_m2m(self):
        pass

    def get_key(self, file: Any) -> str:
        if anchor_settings.ADMIN_UPLOAD_TO:
            dirname = timezone.now().strftime(anchor_settings.ADMIN_UPLOAD_TO)
            return os.path.join(dirname, Blob.generate_key())

        return Blob.generate_key()


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("blob", "name", "order", "content_type", "object_id")
    raw_id_fields = ("blob",)
    list_filter = ("content_type",)
    search_fields = ("id", "object_id", "blob__id")

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
        "human_size",
        "checksum",
        "preview",
        "key",
        "id",
        "created_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("key",),
                    ("filename",),
                    ("mime_type", "human_size", "checksum"),
                    ("preview",),
                    ("id", "created_at"),
                )
            },
        ),
    )

    @admin.display(description="Size", ordering="byte_size")
    def human_size(self, instance: Blob):
        return filesizeformat(instance.byte_size)

    def preview(self, instance: Blob):
        if instance.is_image:
            return format_html(
                '<img src="{}" style="max-width: calc(min(100%, 450px))">',
                instance.url(),
            )

        return "-"

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return AdminBlobForm

        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []

        return super().get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [
                (None, {"fields": ("backend", "file")}),
            ]

        return super().get_fieldsets(request, obj)


@admin.register(VariantRecord)
class VariantRecordAdmin(admin.ModelAdmin):
    list_display = ("blob", "variation_digest")
    raw_id_fields = ("blob",)

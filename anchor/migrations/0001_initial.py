# Generated by Django 5.0.7 on 2024-07-18 08:27

import anchor.models.base
import anchor.models.blob
import anchor.models.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Blob",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=anchor.models.base._gen_short_uuid,
                        editable=False,
                        max_length=22,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "file",
                    anchor.models.fields.VariantFileField(
                        upload_to=anchor.models.blob._attachment_upload_to,
                        verbose_name="file",
                    ),
                ),
                (
                    "alt_text",
                    models.TextField(
                        blank=True,
                        help_text="Provide a description of the file for convenience and accessibility.",
                        null=True,
                        verbose_name="alternative text",
                    ),
                ),
                (
                    "filename",
                    models.CharField(
                        default=None,
                        max_length=256,
                        null=True,
                        verbose_name="original filename",
                    ),
                ),
                (
                    "byte_size",
                    models.PositiveBigIntegerField(
                        blank=True,
                        default=None,
                        help_text="size in bytes",
                        null=True,
                        verbose_name="size",
                    ),
                ),
                (
                    "fingerprint",
                    models.CharField(
                        db_index=True,
                        editable=False,
                        max_length=256,
                        null=True,
                        verbose_name="fingerprint",
                    ),
                ),
                (
                    "mime_type",
                    models.CharField(
                        default="application/octet-stream",
                        editable=False,
                        max_length=32,
                        verbose_name="MIME type",
                    ),
                ),
                (
                    "width",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="original width"
                    ),
                ),
                (
                    "height",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="original height"
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="uploaded by",
                    ),
                ),
            ],
            options={
                "verbose_name": "blob",
                "verbose_name_plural": "blobs",
            },
        ),
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=anchor.models.base._gen_short_uuid,
                        editable=False,
                        max_length=22,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "object_id",
                    models.CharField(
                        db_index=True, max_length=22, verbose_name="object id"
                    ),
                ),
                ("order", models.IntegerField(default=0, verbose_name="order")),
                (
                    "name",
                    models.CharField(
                        default="attachments", max_length=256, verbose_name="name"
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                        verbose_name="content type",
                    ),
                ),
                (
                    "blob",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="attachments",
                        to="anchor.blob",
                        verbose_name="blob",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="attachment",
            constraint=models.UniqueConstraint(
                fields=("content_type", "object_id", "blob", "name"),
                name="unique_attachment_per_blob_and_object_and_name",
            ),
        ),
    ]

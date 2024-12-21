# Generated by Django 5.1.4 on 2024-12-21 12:34

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import anchor.models.base
import anchor.models.blob.representations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
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
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="created at"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "key",
                    models.CharField(
                        editable=False, max_length=256, verbose_name="key"
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
                    "mime_type",
                    models.CharField(
                        default="application/octet-stream",
                        editable=False,
                        max_length=32,
                        verbose_name="MIME type",
                    ),
                ),
                (
                    "backend",
                    models.CharField(
                        default="default",
                        editable=False,
                        max_length=32,
                        verbose_name="backend",
                    ),
                ),
                (
                    "byte_size",
                    models.PositiveBigIntegerField(
                        blank=True,
                        default=None,
                        editable=False,
                        help_text="size in bytes",
                        null=True,
                        verbose_name="size",
                    ),
                ),
                (
                    "checksum",
                    models.CharField(
                        db_index=True,
                        editable=False,
                        max_length=256,
                        null=True,
                        verbose_name="checksum",
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True, default=dict, null=True, verbose_name="metadata"
                    ),
                ),
            ],
            options={
                "verbose_name": "blob",
                "verbose_name_plural": "blobs",
            },
            bases=(
                anchor.models.blob.representations.RepresentationsMixin,
                models.Model,
            ),
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
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="created at"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "object_id",
                    models.CharField(max_length=64, verbose_name="object id"),
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
                        db_index=False,
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
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("content_type", "object_id", "name", "order"),
                        name="unique_attachment_per_content_type_and_object_and_name_and_order",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="VariantRecord",
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
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="created at"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "variation_digest",
                    models.CharField(max_length=32, verbose_name="variation digest"),
                ),
                (
                    "blob",
                    models.ForeignKey(
                        db_index=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variant_records",
                        to="anchor.blob",
                        verbose_name="blob",
                    ),
                ),
            ],
            options={
                "verbose_name": "variant record",
                "verbose_name_plural": "variant records",
                "indexes": [
                    models.Index(
                        fields=["blob", "variation_digest"],
                        name="ix_anchor_records_blob_digest",
                    )
                ],
            },
        ),
    ]

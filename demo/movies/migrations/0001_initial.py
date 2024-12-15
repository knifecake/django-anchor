# Generated by Django 5.1.4 on 2024-12-15 11:38

import anchor.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("anchor", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Movie",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                (
                    "cover",
                    anchor.models.fields.BlobField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                    ),
                ),
                (
                    "poster",
                    anchor.models.fields.BlobField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                    ),
                ),
            ],
        ),
    ]

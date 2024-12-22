from django.contrib import admin

from anchor.forms.widgets import AdminBlobInput
from anchor.models.fields import SingleAttachmentField

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ["title"]

    formfield_overrides = {
        SingleAttachmentField: {
            "widget": AdminBlobInput,
        },
    }

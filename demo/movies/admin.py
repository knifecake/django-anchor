from django.contrib import admin

from .models import Movie
from anchor.admin import AttachmentInline, BlobFieldMixin


@admin.register(Movie)
class MovieAdmin(BlobFieldMixin, admin.ModelAdmin):
    inlines = [AttachmentInline]
    list_display = ["title"]
    search_fields = ["title"]

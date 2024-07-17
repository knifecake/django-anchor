from django.contrib import admin

from .models import Movie
from attachments.admin import AttachmentInline


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    inlines = [AttachmentInline]
    list_display = ["title"]
    search_fields = ["title"]

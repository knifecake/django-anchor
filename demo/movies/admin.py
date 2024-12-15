from django.contrib import admin

from anchor.admin import AttachmentInline

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    inlines = [AttachmentInline]
    list_display = ["title"]
    search_fields = ["title"]

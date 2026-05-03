from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "status", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("status",)
    search_fields = ("name", "description", "owner__email")
    autocomplete_fields = ("owner", "participants")
    readonly_fields = ("created_at",)
    fields = (
        "name",
        "description",
        "owner",
        "github_url",
        "status",
        "participants",
        "created_at",
    )

from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "status",
        "participants_list",
        "created_at",
    )
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

    def get_queryset(self, request):
        """Подтягиваем участников одним запросом, чтобы избежать N+1."""
        return (
            super()
            .get_queryset(request)
            .select_related("owner")
            .prefetch_related("participants")
        )

    @admin.display(description="Участники")
    def participants_list(self, project: Project) -> str:
        """Перечисление участников проекта на странице списка."""
        return ", ".join(
            participant.email for participant in project.participants.all()
        )

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.utils.html import format_html

from .models import User

ADMIN_AVATAR_THUMB_PX = 32


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "name", "surname")


class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreateForm
    form = UserEditForm
    change_password_form = AdminPasswordChangeForm
    model = User

    list_display = (
        "id",
        "avatar_thumb",
        "email",
        "name",
        "surname",
        "is_staff",
        "is_active",
    )
    list_display_links = ("id", "email")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "name", "surname")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {
                "fields": (
                    "name",
                    "surname",
                    "avatar",
                    "about",
                    "phone",
                    "github_url",
                ),
            },
        ),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    readonly_fields = ("date_joined", "last_login")

    @admin.display(description="Аватар")
    def avatar_thumb(self, user: User) -> str:
        """Миниатюра аватара для списка пользователей."""
        if not user.avatar:
            return ""
        return format_html(
            '<img src="{}" width="{}" height="{}" '
            'style="border-radius:50%;object-fit:cover" />',
            user.avatar.url,
            ADMIN_AVATAR_THUMB_PX,
            ADMIN_AVATAR_THUMB_PX,
        )

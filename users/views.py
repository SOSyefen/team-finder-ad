from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from projects.services import paginate

from .forms import (
    ChangePasswordForm,
    EditProfileForm,
    LoginForm,
    RegisterForm,
)
from .models import User

PROJECTS_LIST_REDIRECT = "projects:list"
LOGIN_REDIRECT = "users:login"

FILTER_OWNERS_OF_FAVORITES = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY = "participants-of-my-projects"


def _redirect_authenticated(request):
    if request.user.is_authenticated:
        return redirect(PROJECTS_LIST_REDIRECT)
    return None


def register_view(request):
    if (response := _redirect_authenticated(request)) is not None:
        return response
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(LOGIN_REDIRECT)
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if (response := _redirect_authenticated(request)) is not None:
        return response
    form = LoginForm(request.POST or None, request=request)
    if form.is_valid():
        login(request, form.user)
        return redirect(PROJECTS_LIST_REDIRECT)
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(PROJECTS_LIST_REDIRECT)


def _apply_user_filter(queryset, filter_key: str, current_user):
    """Применяет фильтр списка пользователей по выбранному критерию."""
    if filter_key == FILTER_OWNERS_OF_FAVORITES:
        return queryset.filter(
            owned_projects__in=current_user.favorites.all()
        ).distinct()
    if filter_key == FILTER_OWNERS_OF_PARTICIPATING:
        return queryset.filter(
            owned_projects__in=current_user.participated_projects.all()
        ).distinct()
    if filter_key == FILTER_INTERESTED_IN_MY:
        return queryset.filter(
            favorites__in=current_user.owned_projects.all()
        ).distinct()
    if filter_key == FILTER_PARTICIPANTS_OF_MY:
        return (
            queryset.filter(
                participated_projects__in=current_user.owned_projects.all()
            )
            .exclude(pk=current_user.pk)
            .distinct()
        )
    return queryset


def user_list(request):
    queryset = User.objects.all().order_by("-date_joined")
    active_filter = request.GET.get("filter") or ""
    if active_filter and request.user.is_authenticated:
        queryset = _apply_user_filter(queryset, active_filter, request.user)
    page = paginate(queryset, request)
    return render(
        request,
        "users/participants.html",
        {
            "participants": page.object_list,
            "page_obj": page,
            "active_filter": active_filter,
        },
    )


def user_detail(request, pk):
    target = get_object_or_404(User, pk=pk)
    return render(request, "users/user-details.html", {"user": target})


@login_required
def edit_profile(request):
    form = EditProfileForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if form.is_valid():
        form.save()
        return redirect("users:detail", request.user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", request.user.id)
    return render(request, "users/change_password.html", {"form": form})

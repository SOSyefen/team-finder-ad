from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ChangePasswordForm,
    EditProfileForm,
    LoginForm,
    RegisterForm,
)
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/projects/list/")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/users/login/")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/projects/list/")
    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.user)
            return redirect("/projects/list/")
    else:
        form = LoginForm(request=request)
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


def user_list(request):
    qs = User.objects.all().order_by("-date_joined")
    active_filter = request.GET.get("filter") or ""

    if active_filter and request.user.is_authenticated:
        u = request.user
        if active_filter == "owners-of-favorite-projects":
            qs = qs.filter(owned_projects__in=u.favorites.all()).distinct()
        elif active_filter == "owners-of-participating-projects":
            qs = qs.filter(
                owned_projects__in=u.participated_projects.all()
            ).distinct()
        elif active_filter == "interested-in-my-projects":
            qs = qs.filter(favorites__in=u.owned_projects.all()).distinct()
        elif active_filter == "participants-of-my-projects":
            qs = (
                qs.filter(participated_projects__in=u.owned_projects.all())
                .exclude(pk=u.pk)
                .distinct()
            )

    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page"))
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
    if request.method == "POST":
        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user
        )
        if form.is_valid():
            form.save()
            return redirect(f"/users/{request.user.id}/")
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f"/users/{request.user.id}/")
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})

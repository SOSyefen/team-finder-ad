from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


def project_list(request):
    qs = Project.objects.all().order_by("-created_at")
    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/project_list.html",
        {"projects": page.object_list, "page_obj": page},
    )


@login_required
def favorite_projects(request):
    qs = request.user.favorites.all().order_by("-created_at")
    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": page.object_list, "page_obj": page},
    )


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(
        request, "projects/project-details.html", {"project": project}
    )


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm()
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return redirect(f"/projects/{project.id}/")
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "forbidden"}, status=403)
    if project.status != "open":
        return JsonResponse(
            {"status": "error", "project_status": project.status}, status=400
        )
    project.status = "closed"
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        return JsonResponse({"status": "ok", "participant": False})
    project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": True})


@login_required
@require_POST
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        return JsonResponse({"status": "ok", "favorited": False})
    request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": True})

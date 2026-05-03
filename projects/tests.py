import json

from django.test import Client, TestCase
from django.urls import reverse

from users.models import User

from .models import Project


class ProjectListAndDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="qwerty12345",
            name="Own",
            surname="Er",
        )
        cls.project = Project.objects.create(
            name="Test Project",
            description="desc",
            owner=cls.owner,
        )

    def test_anonymous_can_view_project_list(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_can_view_project_detail(self):
        response = self.client.get(
            reverse("projects:detail", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_anonymous_cannot_create_project(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response["Location"])


class ProjectCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="creator@example.com",
            password="qwerty12345",
            name="Cre",
            surname="At",
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_create_project_assigns_owner(self):
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "Brand new",
                "description": "x",
                "github_url": "https://github.com/owner/repo",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="Brand new")
        self.assertEqual(project.owner, self.user)
        self.assertIn(self.user, project.participants.all())

    def test_create_project_rejects_non_github_url(self):
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "Bad",
                "description": "x",
                "github_url": "https://gitlab.com/foo",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "github")


class AjaxEndpointsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="ajaxowner@example.com",
            password="qwerty12345",
            name="O",
            surname="O",
        )
        self.other = User.objects.create_user(
            email="ajaxother@example.com",
            password="qwerty12345",
            name="X",
            surname="X",
        )
        self.project = Project.objects.create(
            name="Ajax target",
            owner=self.owner,
        )

    def _post_json(self, url):
        response = self.client.post(url)
        self.assertEqual(response["Content-Type"], "application/json")
        return response.status_code, json.loads(response.content)

    def test_toggle_favorite(self):
        self.client.force_login(self.other)
        url = reverse("projects:toggle_favorite", args=[self.project.pk])
        status, data = self._post_json(url)
        self.assertEqual(status, 200)
        self.assertTrue(data["favorited"])
        status, data = self._post_json(url)
        self.assertFalse(data["favorited"])

    def test_toggle_participate(self):
        self.client.force_login(self.other)
        url = reverse("projects:toggle_participate", args=[self.project.pk])
        status, data = self._post_json(url)
        self.assertTrue(data["participant"])
        status, data = self._post_json(url)
        self.assertFalse(data["participant"])

    def test_complete_only_owner(self):
        self.client.force_login(self.other)
        url = reverse("projects:complete", args=[self.project.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.owner)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "closed")


class FavoriteAndFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="favuser@example.com",
            password="qwerty12345",
            name="F",
            surname="U",
        )
        self.peer = User.objects.create_user(
            email="peer@example.com",
            password="qwerty12345",
            name="UniquePeerName",
            surname="UniquePeerSurname",
        )
        self.peer_project = Project.objects.create(
            name="Peers project",
            owner=self.peer,
        )
        self.client.force_login(self.user)

    def test_favorites_page_lists_favorited_projects(self):
        self.user.favorites.add(self.peer_project)
        response = self.client.get(reverse("projects:favorites"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Peers project")

    def test_user_filter_owners_of_favorite_projects(self):
        self.user.favorites.add(self.peer_project)
        response = self.client.get(
            reverse("users:list") + "?filter=owners-of-favorite-projects"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "UniquePeerName")

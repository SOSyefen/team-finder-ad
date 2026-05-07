import json
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from users.models import User

from .constants import STATUS_CLOSED, STATUS_OPEN
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
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_can_view_project_detail(self):
        response = self.client.get(
            reverse("projects:detail", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_cannot_create_project(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("users:login"), response["Location"])


class ProjectCreateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="creator@example.com",
            password="qwerty12345",
            name="Cre",
            surname="At",
        )
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_create_project_assigns_owner(self):
        response = self.user_client.post(
            reverse("projects:create"),
            {
                "name": "Brand new",
                "description": "x",
                "github_url": "https://github.com/owner/repo",
                "status": STATUS_OPEN,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        project = Project.objects.get(name="Brand new")
        self.assertEqual(project.owner, self.user)
        self.assertIn(self.user, project.participants.all())

    def test_create_project_rejects_non_github_url(self):
        response = self.user_client.post(
            reverse("projects:create"),
            {
                "name": "Bad",
                "description": "x",
                "github_url": "https://gitlab.com/foo",
                "status": STATUS_OPEN,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "github")


class AjaxEndpointsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="ajaxowner@example.com",
            password="qwerty12345",
            name="O",
            surname="O",
        )
        cls.other = User.objects.create_user(
            email="ajaxother@example.com",
            password="qwerty12345",
            name="X",
            surname="X",
        )
        cls.owner_client = Client()
        cls.owner_client.force_login(cls.owner)
        cls.other_client = Client()
        cls.other_client.force_login(cls.other)

    def setUp(self):
        # Сам объект пересоздаём в setUp, потому что некоторые тесты
        # меняют статус проекта; так каждый тест получает свежий project.
        self.project = Project.objects.create(
            name="Ajax target",
            owner=self.owner,
        )

    def _post_json(self, client, url):
        response = client.post(url)
        self.assertEqual(response["Content-Type"], "application/json")
        return response.status_code, json.loads(response.content)

    def test_toggle_favorite(self):
        url = reverse("projects:toggle_favorite", args=[self.project.pk])
        status, data = self._post_json(self.other_client, url)
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(data["favorited"])
        status, data = self._post_json(self.other_client, url)
        self.assertFalse(data["favorited"])

    def test_toggle_participate(self):
        url = reverse("projects:toggle_participate", args=[self.project.pk])
        status, data = self._post_json(self.other_client, url)
        self.assertTrue(data["participant"])
        status, data = self._post_json(self.other_client, url)
        self.assertFalse(data["participant"])

    def test_complete_only_owner(self):
        url = reverse("projects:complete", args=[self.project.pk])
        response = self.other_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

        response = self.owner_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, STATUS_CLOSED)


class FavoriteAndFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="favuser@example.com",
            password="qwerty12345",
            name="F",
            surname="U",
        )
        cls.peer = User.objects.create_user(
            email="peer@example.com",
            password="qwerty12345",
            name="UniquePeerName",
            surname="UniquePeerSurname",
        )
        cls.peer_project = Project.objects.create(
            name="Peers project",
            owner=cls.peer,
        )
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_favorites_page_lists_favorited_projects(self):
        self.user.favorites.add(self.peer_project)
        response = self.user_client.get(reverse("projects:favorites"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Peers project")

    def test_user_filter_owners_of_favorite_projects(self):
        self.user.favorites.add(self.peer_project)
        response = self.user_client.get(
            reverse("users:list") + "?filter=owners-of-favorite-projects"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "UniquePeerName")

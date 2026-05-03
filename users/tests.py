from django.test import Client, TestCase
from django.urls import reverse

from .models import User, normalize_phone


class UserModelTests(TestCase):
    def test_create_user_generates_avatar(self):
        user = User.objects.create_user(
            email="alice@example.com",
            password="qwerty12345",
            name="Alice",
            surname="Wonder",
        )
        self.assertTrue(user.avatar.name)
        self.assertTrue(user.check_password("qwerty12345"))

    def test_phone_is_normalized_on_save(self):
        user = User.objects.create_user(
            email="bob@example.com",
            password="qwerty12345",
            name="Bob",
            surname="X",
            phone="89991234567",
        )
        self.assertEqual(user.phone, "+79991234567")

    def test_normalize_phone_helper(self):
        self.assertEqual(normalize_phone("89991234567"), "+79991234567")
        self.assertEqual(normalize_phone("+79991234567"), "+79991234567")

    def test_create_superuser_has_staff_flag(self):
        admin = User.objects.create_superuser(
            email="root@example.com",
            password="rootpass1234",
            name="Root",
            surname="Admin",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="login@example.com",
            password="qwerty12345",
            name="Log",
            surname="In",
        )

    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "New",
                "surname": "User",
                "email": "newuser@example.com",
                "password": "qwerty12345",
            },
        )
        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(
            User.objects.filter(email="newuser@example.com").exists()
        )

    def test_register_rejects_duplicate_email(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Dup",
                "surname": "User",
                "email": "login@example.com",
                "password": "qwerty12345",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже существует")

    def test_login_and_logout(self):
        response = self.client.post(
            reverse("users:login"),
            {"email": "login@example.com", "password": "qwerty12345"},
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        response = self.client.post(
            reverse("users:login"),
            {"email": "login@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный")


class EditProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="edit@example.com",
            password="qwerty12345",
            name="Edit",
            surname="Me",
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_edit_profile_rejects_non_github_url(self):
        response = self.client.post(
            reverse("users:edit_profile"),
            {
                "name": "Edit",
                "surname": "Me",
                "github_url": "https://gitlab.com/me",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "github")

    def test_edit_profile_normalizes_phone(self):
        self.client.post(
            reverse("users:edit_profile"),
            {
                "name": "Edit",
                "surname": "Me",
                "phone": "89998887766",
                "github_url": "https://github.com/me",
            },
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79998887766")

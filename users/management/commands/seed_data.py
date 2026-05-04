"""Команда для наполнения базы данных демо-данными.

Источник данных — JSON-файл, путь по умолчанию `users/management/commands/data/seed.json`.
Можно передать свой файл флагом `--file`.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from projects.models import Project
from users.models import User

DEFAULT_DATA_FILE = Path(__file__).parent / "data" / "seed.json"


class Command(BaseCommand):
    help = "Seed the database with demo users and projects from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=Path,
            default=DEFAULT_DATA_FILE,
            help="Path to the JSON file with seed data.",
        )

    def handle(self, *args, **options):
        data_file: Path = options["file"]
        if not data_file.exists():
            raise CommandError(f"Seed file not found: {data_file}")

        with data_file.open(encoding="utf-8") as fh:
            data = json.load(fh)

        self._seed_users(data.get("users", []))
        self._seed_projects(data.get("projects", []))
        self._seed_superuser(data.get("superuser"))

        self.stdout.write(self.style.SUCCESS("Done."))

    def _seed_users(self, users):
        for record in users:
            user, created = User.objects.get_or_create(
                email=record["email"],
                defaults={
                    "name": record["name"],
                    "surname": record["surname"],
                    "phone": record.get("phone") or None,
                    "about": record.get("about", ""),
                    "github_url": record.get("github_url", ""),
                },
            )
            if created:
                user.set_password(record["password"])
                user.save()
                self._ok(f"Created user {user.email}")
            else:
                self.stdout.write(f"User {user.email} already exists")

    def _seed_projects(self, projects):
        for record in projects:
            owner = User.objects.get(email=record["owner_email"])
            project, created = Project.objects.get_or_create(
                name=record["name"],
                owner=owner,
                defaults={
                    "description": record.get("description", ""),
                    "status": record.get("status", "open"),
                    "github_url": record.get("github_url", ""),
                },
            )
            project.participants.add(owner)
            if created:
                self._ok(f"Created project {project.name}")
            else:
                self.stdout.write(f"Project {project.name} already exists")

    def _seed_superuser(self, record):
        if not record:
            return
        if User.objects.filter(is_superuser=True).exists():
            return
        User.objects.create_superuser(
            email=record["email"],
            password=record["password"],
            name=record["name"],
            surname=record["surname"],
        )
        self._ok(
            f"Created superuser {record['email']} / {record['password']}"
        )

    def _ok(self, message: str) -> None:
        self.stdout.write(self.style.SUCCESS(message))

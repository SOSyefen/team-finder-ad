# TeamFinder

Веб-платформа для поиска команды для pet-проектов: разработчики, дизайнеры и
другие специалисты могут публиковать идеи, находить единомышленников и
откликаться на предложения.

Проект реализован по **Варианту 1** (избранное проектов + фильтрация
пользователей по 4 критериям).

## Стек технологий

- Python 3.11
- Django 5.2.4
- PostgreSQL 16
- Pillow (генерация дефолтных аватарок)
- python-decouple (работа с .env)
- Docker / docker-compose (поднятие БД)

## Структура

```
team-finder-ad/
├── team_finder/        # настройки Django-проекта
├── users/              # приложение пользователей: модель User, регистрация,
│                       # логин, профиль, фильтр пользователей
├── projects/           # приложение проектов: CRUD проектов, избранное,
│                       # участие, AJAX-эндпоинты
├── templates_var1/     # HTML-шаблоны (Вариант 1)
├── static/             # CSS, JS, шрифты, картинки
├── media/              # пользовательский контент (аватарки) — генерируется
│                       # автоматически
├── docker-compose.yml  # сервис PostgreSQL
├── requirements.txt
└── .env_example        # шаблон переменных окружения
```

## Локальный запуск

### 1. Клонировать репозиторий и перейти в папку

```bash
git clone <url> team-finder-ad
cd team-finder-ad
```

### 2. Создать виртуальное окружение

Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env`

Скопировать `.env_example` в `.env` и заполнить:

```bash
cp .env_example .env
```

Все ключи `.env`:

| Переменная            | Назначение                                           |
|-----------------------|------------------------------------------------------|
| `DJANGO_SECRET_KEY`   | Секретный ключ Django (можно сгенерировать через `django.core.management.utils.get_random_secret_key`) |
| `DJANGO_DEBUG`        | `True` для разработки, `False` для прода             |
| `POSTGRES_DB`         | имя БД                                               |
| `POSTGRES_USER`       | пользователь БД                                      |
| `POSTGRES_PASSWORD`   | пароль БД                                            |
| `POSTGRES_HOST`       | `localhost` для локальной разработки                 |
| `POSTGRES_PORT`       | `5432`                                               |
| `TASK_VERSION`        | **`1`** — задаёт папку шаблонов `templates_var1`     |

### 5. Запустить PostgreSQL

```bash
docker compose up -d
```

### 6. Применить миграции и засеять тестовые данные

```bash
python manage.py migrate
python manage.py seed_data
```

Команда `seed_data` создаст:
- 4 обычных пользователя (см. ниже),
- 4 проекта (по одному у каждого пользователя),
- суперпользователя `admin@example.com / admin12345`.

### 7. Запустить сервер разработки

```bash
python manage.py runserver
```

Приложение откроется на `http://localhost:8000`.

## Тестовые учётные записи

| Email                 | Пароль        | Роль          |
|-----------------------|---------------|---------------|
| admin@example.com     | admin12345    | Администратор |
| maria@yandex.ru       | password      | Пользователь  |
| ivan@example.com      | password123   | Пользователь  |
| anna@example.com      | password123   | Пользователь  |
| oleg@example.com      | password123   | Пользователь  |

## Особенности реализации

- Кастомная модель `User` с полем `email` в качестве `USERNAME_FIELD`
  (`users.User`).
- При создании пользователя без аватара аватар генерируется автоматически:
  первая буква имени на однотонном цветном фоне (см. `users/avatar.py`).
- Телефон валидируется и нормализуется к формату `+7XXXXXXXXXX`
  (форматы `8XXXXXXXXXX` приводятся к `+7...` при сохранении).
- Поле `github_url` в моделях `User` и `Project` дополнительно валидируется
  на принадлежность домену `github.com`.
- Главная страница `/` редиректит на `/projects/list/`.
- Пагинация по 12 элементов на страницах проектов и пользователей.
- Фильтрация пользователей по 4 критериям (`?filter=...`):
  - `owners-of-favorite-projects`
  - `owners-of-participating-projects`
  - `interested-in-my-projects`
  - `participants-of-my-projects`
- AJAX-эндпоинты возвращают JSON в форматах, ожидаемых JS:
  - `POST /projects/<id>/toggle-favorite/` → `{"status": "ok", "favorited": bool}`
  - `POST /projects/<id>/toggle-participate/` → `{"status": "ok", "participant": bool}`
  - `POST /projects/<id>/complete/` → `{"status": "ok", "project_status": "closed"}`

## Админка

Доступна по адресу `/admin/`. Через админку можно:
- управлять пользователями (создание, блокировка, смена пароля);
- редактировать и удалять проекты любых пользователей.

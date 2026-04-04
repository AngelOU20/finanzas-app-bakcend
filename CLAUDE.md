# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal finance backend API built with Django 6 and Django REST Framework. Currently implements user authentication; additional financial features are planned as separate Django apps.

## Commands

### Running the development server
```bash
python manage.py runserver
```

### Database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Running tests
```bash
pytest                          # all tests
pytest users/tests/             # single app
pytest users/tests/test_auth.py # single file
pytest -v                       # verbose
pytest -k "test_successful"     # filter by name
```

### API Documentation
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Architecture

### Tech Stack
- **Django 6 / DRF** — REST API framework
- **MySQL** — primary database (configured via `.env`)
- **JWT (simplejwt)** — stateless authentication with token rotation and blacklisting
- **drf-spectacular** — auto-generated OpenAPI 3.0 docs (Swagger + ReDoc, served via sidecar — no CDN)
- **pytest-django** — test runner

### URL Structure
All API routes are versioned under `/api/v0/`. Current routes:
- `POST /api/v0/users/register/` — create account
- `POST /api/v0/users/login/` — obtain JWT tokens
- `POST /api/v0/users/login/refresh/` — rotate access token
- `POST /api/v0/users/logout/` — blacklist refresh token

### App Structure Pattern
Each Django app follows this layout:
```
app/
  models.py          # ORM models
  views.py           # API views (thin — delegate to services)
  services.py        # business logic (receive DTOs, return model instances)
  types.py           # dataclass DTOs for service inputs
  serializers/
    request.py       # input validation serializers
    response.py      # response serializers (used in OpenAPI docs)
  schemas.py         # drf-spectacular @extend_schema decorators
  urls.py
  tests/
    conftest.py      # pytest fixtures
    test_*.py
  factories.py       # factory_boy factories for tests
```

### Key Patterns

**JWT configuration** — access tokens: 15 min, refresh tokens: 1 day. Rotation and blacklisting are enabled (`rest_framework_simplejwt.token_blacklist` is in INSTALLED_APPS and must be migrated).

**Throttling** — `AnonRateThrottle` (50/min), `UserRateThrottle` (100/min) apply globally. Login endpoint uses `ScopedRateThrottle` at 5/min.

**DTOs** — services receive typed `@dataclass` DTOs (defined in `types.py`), not raw serializer data. Views extract fields from validated serializer data and build DTOs before calling services.

**OpenAPI schemas** — endpoint documentation lives in `schemas.py` as `@extend_schema` calls. Apply them to views via `@extend_schema(**schema_name)` or as a decorator.

**Custom User model** — `users.User` extends `AbstractUser`, adding a unique `email` field and a `Role` choice field (`ADMIN` / `USER`). `AUTH_USER_MODEL = "users.User"`.

### Environment
Configured via `.env` at the project root. Required variables:
```
SECRET_KEY, DEBUG, ENV_STATE
DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
```

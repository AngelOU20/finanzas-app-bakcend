# Finanzas App — Backend

API REST para gestión de finanzas personales, construida con Django 6 y Django REST Framework. Actualmente implementa autenticación completa con JWT; las funcionalidades financieras se agregarán como apps Django separadas.

## Stack

| Tecnología | Versión | Rol |
|---|---|---|
| Python | 3.12+ | Lenguaje |
| Django | 6.0 | Framework web |
| Django REST Framework | 3.17 | API REST |
| Simple JWT | 5.5 | Autenticación JWT |
| drf-spectacular | 0.29 | Documentación OpenAPI 3.0 |
| MySQL | 8+ | Base de datos |
| pytest-django | 4.12 | Runner de tests |
| django-cors-headers | 4.9 | CORS para el frontend |

## Requisitos previos

- Python 3.12+
- MySQL 8+
- pip

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd finanzas-app-backend

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores (ver sección Variables de entorno)

# 5. Crear la base de datos en MySQL
mysql -u root -p -e "CREATE DATABASE finanzas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 6. Aplicar migraciones
python manage.py migrate

# 7. Levantar el servidor
python manage.py runserver
```

## Variables de entorno

Copiar `.env.example` como `.env` y completar los valores. El archivo `.env` nunca se sube al repositorio.

| Variable | Descripción | Ejemplo |
|---|---|---|
| `ENV_STATE` | Entorno actual | `local` \| `production` |
| `DEBUG` | Modo debug | `True` (solo en local) |
| `SECRET_KEY` | Clave secreta de Django | `django-insecure-...` |
| `ALLOWED_HOSTS` | Hosts permitidos (JSON array) | `["localhost", "127.0.0.1"]` |
| `CORS_ALLOWED_ORIGINS` | Orígenes del frontend (JSON array) | `["http://localhost:5173"]` |
| `DB_NAME` | Nombre de la base de datos | `finanzas_db` |
| `DB_USER` | Usuario de MySQL | `root` |
| `DB_PASSWORD` | Contraseña de MySQL | `tu_password` |
| `DB_HOST` | Host de MySQL | `127.0.0.1` |
| `DB_PORT` | Puerto de MySQL | `3306` |
| `PASSSUPERUSER` | Contraseña del superusuario de seeding | `tu_password` |

## Endpoints

Base URL: `http://localhost:8000/api/v0/`

### Autenticación (`/users/`)

| Método | Endpoint | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/users/register/` | Registrar nuevo usuario | No |
| `POST` | `/users/login/` | Obtener tokens JWT | No |
| `POST` | `/users/login/refresh/` | Renovar access token | No |
| `POST` | `/users/logout/` | Invalidar refresh token | Si (Bearer) |

### Registro — `POST /users/register/`

**Request:**
```json
{
  "username": "juliou",
  "email": "julio@email.com",
  "password": "MiPassword123!",
  "role": "USER"
}
```

**Response `201`:**
```json
{
  "message": "Usuario creado con éxito",
  "user": {
    "id": 1,
    "username": "juliou",
    "email": "julio@email.com",
    "role": "USER"
  }
}
```

### Login — `POST /users/login/`

Limitado a 5 intentos por minuto por IP.

**Request:**
```json
{
  "username": "juliou",
  "password": "MiPassword123!"
}
```

**Response `200`:**
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>",
  "user": {
    "id": 1,
    "username": "juliou",
    "email": "julio@email.com",
    "role": "USER"
  }
}
```

### Refresh — `POST /users/login/refresh/`

**Request:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response `200`:**
```json
{
  "access": "<nuevo_access_token>",
  "refresh": "<nuevo_refresh_token>"
}
```

### Logout — `POST /users/logout/`

Requiere header `Authorization: Bearer <access_token>`.

**Request:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response `204`:** sin cuerpo.

## Autenticación JWT

Los tokens se envían en el header HTTP:

```
Authorization: Bearer <access_token>
```

| Token | Duración | Rotación |
|---|---|---|
| Access | 15 minutos | No (se renueva con refresh) |
| Refresh | 1 día | Si (cada uso genera uno nuevo) |

Al hacer logout, el refresh token se agrega a una blacklist y queda inutilizable.

## Throttling

| Scope | Límite |
|---|---|
| Anónimo (global) | 50 req/min |
| Autenticado (global) | 100 req/min |
| Login | 5 req/min por IP |

## Documentación interactiva

Con el servidor levantado:

- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`
- **OpenAPI schema (JSON):** `http://localhost:8000/api/schema/`

La documentación se sirve con assets locales (sin CDN), via `drf-spectacular-sidecar`.

## Tests

```bash
pytest                              # todos los tests
pytest users/tests/                 # solo la app users
pytest users/tests/test_auth.py     # un archivo específico
pytest -v                           # verbose
pytest -k "test_register"           # filtrar por nombre
```

Los tests usan `factory_boy` para generar datos y sobreescriben los límites de throttling para evitar falsos 429.

## Estructura del proyecto

```
finanzas-app-backend/
├── config/
│   ├── settings.py       # Configuración global
│   ├── urls.py           # URLs raíz
│   └── wsgi.py
├── users/                # App de autenticación
│   ├── models.py         # Modelo User personalizado
│   ├── views.py          # Vistas (delegan a services)
│   ├── services.py       # Lógica de negocio
│   ├── types.py          # DTOs (dataclasses)
│   ├── schemas.py        # Decoradores OpenAPI
│   ├── factories.py      # Factories para tests
│   ├── serializers/
│   │   ├── request.py    # Validación de entrada
│   │   └── response.py   # Formato de salida
│   ├── tests/
│   │   ├── conftest.py   # Fixtures globales
│   │   └── test_auth.py
│   └── urls.py
├── .env                  # Variables de entorno (no se sube al repo)
├── .env.example          # Plantilla de variables de entorno
├── requirements.txt
└── manage.py
```

## Modelo de usuario

Extiende `AbstractUser` de Django con dos campos adicionales:

| Campo | Tipo | Descripción |
|---|---|---|
| `email` | EmailField (unique) | Reemplaza al email base de Django |
| `role` | CharField (choices) | `ADMIN` o `USER` (default: `USER`) |

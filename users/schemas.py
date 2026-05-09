from typing import Any, Callable

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema

from .serializers import (
    ChangePasswordSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
    MeResponseSerializer,
    RegisterResponseSerializer,
    UserRegistrationSerializer,
)

# ESQUEMA DE REGISTRO
register_user_schema: Callable[[Callable[..., Any]], Callable[..., Any]] = (
    extend_schema(
        summary="Registrar un nuevo usuario",
        description="Crea un usuario en el sistema. El rol se asigna automáticamente como USER.",
        request=UserRegistrationSerializer,
        tags=["Autenticación"],
        examples=[
            OpenApiExample(
                name="Valid Registration Example",
                description="Standard data for creating a new user.",
                value={
                    "username": "johndoe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "johndoe@example.com",
                    "password": "SecurePassword123",
                    "password_confirm": "SecurePassword123",
                },
                request_only=True,
            )
        ],
        responses={
            201: RegisterResponseSerializer,
            400: OpenApiResponse(
                description="Error de validación en los datos enviados.",
                response={"type": "object"},
                examples=[
                    OpenApiExample(
                        name="Email duplicado",
                        value={
                            "email": ["Usuario con este correo electrónico ya existe."]
                        },
                    ),
                    OpenApiExample(
                        name="Faltan campos",
                        value={"username": ["Este campo es obligatorio."]},
                    ),
                    OpenApiExample(
                        name="Contraseñas no coinciden",
                        value={"password_confirm": ["Las contraseñas no coinciden."]},
                    ),
                ],
            ),
        },
    )
)

# ESQUEMA DE LOGIN
login_user_schema = extend_schema(
    summary="Iniciar sesión (Obtener Tokens)",
    description="Autentica a un usuario usando sus credenciales. Devuelve los tokens JWT (access y refresh) junto con los datos básicos.",
    tags=["Autenticación"],
    examples=[
        OpenApiExample(
            name="Valid Login Example",
            description="Datos de ejemplo para iniciar sesión con éxito.",
            value={"username": "johndoe", "password": "SecurePassword123"},
            request_only=True,
        )
    ],
    responses={
        200: LoginResponseSerializer,
        401: OpenApiResponse(description="Credenciales incorrectas o cuenta inactiva."),
    },
)

# ESQUEMA DE LOGOUT
logout_user_schema: Callable[[Callable[..., Any]], Callable[..., Any]] = extend_schema(
    summary="Cerrar sesión (Logout)",
    description="Cierra la sesión del usuario actual invalidando su Refresh Token.",
    tags=["Autenticación"],
    request=LogoutSerializer,
    responses={
        204: OpenApiResponse(
            description="Sesión cerrada exitosamente, token invalidado."
        ),
        400: OpenApiResponse(
            description="Error en la solicitud, token inválido o faltante."
        ),
    },
)

# ESQUEMA DE /me
me_schema: Callable[[Callable[..., Any]], Callable[..., Any]] = extend_schema(
    summary="Obtener perfil del usuario autenticado",
    description="Devuelve los datos del usuario asociado al token de acceso enviado en el header Authorization.",
    tags=["Usuarios"],
    responses={
        200: MeResponseSerializer,
        401: OpenApiResponse(description="Token de acceso inválido, expirado o ausente."),
    },
)

# ESQUEMA DE CAMBIO DE CONTRASEÑA
change_password_schema: Callable[[Callable[..., Any]], Callable[..., Any]] = (
    extend_schema(
        summary="Cambiar contraseña del usuario autenticado",
        description="Permite al usuario autenticado cambiar su contraseña proporcionando la actual y la nueva (confirmada).",
        tags=["Usuarios"],
        request=ChangePasswordSerializer,
        responses={
            204: OpenApiResponse(description="Contraseña actualizada correctamente."),
            400: OpenApiResponse(
                description="Error de validación: contraseña actual incorrecta, nueva contraseña no válida o no coincide con la confirmación.",
                response={"type": "object"},
                examples=[
                    OpenApiExample(
                        name="Contraseña actual incorrecta",
                        value={"old_password": ["La contraseña actual es incorrecta."]},
                    ),
                    OpenApiExample(
                        name="Contraseñas nuevas no coinciden",
                        value={
                            "new_password_confirm": ["Las contraseñas no coinciden."]
                        },
                    ),
                    OpenApiExample(
                        name="Nueva igual a la actual",
                        value={
                            "new_password": [
                                "La contraseña nueva debe ser distinta de la actual."
                            ]
                        },
                    ),
                ],
            ),
            401: OpenApiResponse(description="Token de acceso inválido o ausente."),
        },
    )
)

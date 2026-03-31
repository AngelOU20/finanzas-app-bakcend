from typing import Any, Callable
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .serializers import UserRegistrationSerializer


register_user_schema: Callable[[Callable[..., Any]], Callable[..., Any]] = extend_schema(
    summary='Registrar un nuevo usuario',
    description='Crea un usuario en el sistema con un rol específico (ADMIN o USER).',
    request=UserRegistrationSerializer,
    tags=['Gestión de Usuarios'],
    examples=[
        OpenApiExample(
            name='Ejemplo de Registro',
            value={
                "username": "juan_perez",
                "first_name": "Juan",
                "last_name": "Perez",
                "email": "juan@gmail.com",
                "password": "MiPasswordSeguro123",
                "password_confirm": "MiPasswordSeguro123",
                "role": "USER"
            },
            request_only=True
        )
    ],
    responses={
        201: OpenApiResponse(
            description='Usuario creado exitosamente.',
            response={
                'type': 'object',
                'properties': {
                    'mensaje': {'type': 'string'},
                    'usuario': {
                        'type': 'object',
                        'properties': {
                            'username': {'type': 'string'},
                            'first_name': {'type': 'string'},
                            'last_name': {'type': 'string'},
                            'email': {'type': 'string'},
                            'role': {'type': 'string'}
                        }
                    }
                }
            },
            examples=[
                OpenApiExample(
                    name='Registro Exitoso',
                    value={
                        "mensaje": "Usuario creado con éxito",
                        "usuario": {
                            "username": "nuevo_cliente",
                            "first_name": "Nuevo",
                            "last_name": "Cliente",
                            "email": "cliente@gmail.com",
                            "role": "USER"
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Error de validación en los datos enviados.',
            response={'type': 'object'},
            examples=[
                OpenApiExample(
                    name='Email duplicado',
                    value={
                        "email": ["Usuario con este correo electrónico ya existe."]
                    }
                ),
                OpenApiExample(
                    name='Faltan campos',
                    value={
                        "username": ["Este campo es obligatorio."]
                    }
                ),
                OpenApiExample(
                    name='Contraseñas no coinciden',
                    value={
                        "password_confirm": ["Las contraseñas no coinciden."]
                    }
                )
            ]
        ),
    }
)
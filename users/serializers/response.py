from rest_framework import serializers

from users.models import User


class UserDetailResponseSerializer(serializers.ModelSerializer):
    """
    Serializer de salida reutilizable para representar datos básicos de un usuario.
    Usado en respuestas de registro y cualquier endpoint que retorne info de usuario.
    """

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role"]


# --- Login ---


class LoginUserDetailSerializer(serializers.Serializer):
    """
    Serializer de salida para los datos del usuario dentro de la respuesta de login.
    Se define aparte de UserDetailResponseSerializer porque incluye campos
    adicionales (id, is_active) que son relevantes solo al autenticarse.
    """

    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.CharField()
    is_active = serializers.BooleanField()


class LoginResponseSerializer(serializers.Serializer):
    """Serializer de salida para la respuesta completa del login (solo Swagger)."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = LoginUserDetailSerializer()


# --- Registro ---


class RegisterResponseSerializer(serializers.Serializer):
    """
    Serializer de salida para la respuesta del registro.
    Reutiliza UserDetailResponseSerializer en lugar de duplicar campos.
    """

    message = serializers.CharField(default="Usuario creado con éxito")
    user = UserDetailResponseSerializer()  # ← reutiliza el ModelSerializer, no duplica

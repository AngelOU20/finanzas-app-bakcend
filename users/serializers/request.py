from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.serializers.response import LoginUserDetailSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de usuarios. Permite crear un nuevo usuario con un nombre de usuario,
    correo electrónico y contraseña. El rol no se expone: todos los registros públicos son siempre USER.

    Se extiende de ModelSerializer (en lugar de Serializer plano) para aprovechar la validación
    automática de campos del modelo: unicidad de email/username, max_length, etc. Sin embargo,
    create() está bloqueado intencionalmente — la creación se delega a la capa de servicios.
    """

    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}, label="Confirmar Contraseña"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
        ]

    def create(self, validated_data):
        raise NotImplementedError(
            "La creación de usuarios se maneja en la capa de servicios, no en el serializer. Usa create_user() del service."
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        """
        Validación personalizada para asegurar que las contraseñas coincidan. Si las contraseñas no coinciden, se lanza un error de validación.
        """
        # Extraemos el campo password
        password = attrs.get("password")
        # Extraemos el campo password_confirm para compararlo con password, pero lo eliminamos de attrs para que no se intente guardar en el modelo
        password_confirm = attrs.pop("password_confirm", None)

        if password != password_confirm:
            # Si las contraseñas no coinciden, lanzamos un error de validación con un mensaje específico
            raise serializers.ValidationError(
                {"password_confirm": "Las contraseñas no coinciden."}
            )

        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT. Este serializer se utiliza para personalizar la respuesta del endpoint de login, incluyendo información adicional del usuario junto con los tokens.
    """

    default_error_messages = {
        "no_active_account": "Credenciales incorrectas o la cuenta está inactiva."
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = LoginUserDetailSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    """
    Serializer para el logout de usuarios. Este serializer se utiliza para validar el token de refresh que se enviará para invalidar el token de acceso.
    """

    refresh = serializers.CharField(
        help_text="Token de refresh que se enviará para invalidar el token de acceso."
    )

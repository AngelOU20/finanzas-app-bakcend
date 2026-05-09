from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .types import ChangePasswordDTO, UserCreateDTO


def create_user(data: UserCreateDTO) -> User:
    """
    Crea un nuevo usuario en la base de datos utilizando los datos proporcionados en el DTO. El DTO debe contener el nombre de usuario, correo electrónico, contraseña y rol del usuario. La función devuelve el usuario creado.
    """
    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        password=data.password,
        role=data.role,
    )
    return user


def logout_user(refresh_token: str) -> None:
    """
    Invalida el refresh token agregándolo a la lista negra.
    Lanza TokenError / InvalidToken si el token es inválido o ya fue blacklisteado.
    """
    token = RefreshToken(refresh_token)
    token.blacklist()


def change_password(data: ChangePasswordDTO) -> None:
    """
    Cambia la contraseña del usuario. Asume que la nueva contraseña ya pasó
    por los validadores y que la actual ya fue verificada en el serializer.
    """
    data.user.set_password(data.new_password)
    data.user.save(update_fields=["password"])

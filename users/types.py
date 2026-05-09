from dataclasses import dataclass

from .models import User


@dataclass
class UserCreateDTO:
    """
    Data Transfer Object para la creación de un nuevo usuario.
    """

    username: str
    first_name: str
    last_name: str
    email: str
    password: str
    role: User.Role = User.Role.USER


@dataclass
class ChangePasswordDTO:
    """
    Data Transfer Object para el cambio de contraseña de un usuario autenticado.
    """

    user: User
    new_password: str

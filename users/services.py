from .models import User
from .types import UserCreateDTO


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
    role=data.role
  )
  return user
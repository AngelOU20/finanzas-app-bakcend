from dataclasses import dataclass


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
  role: str = 'USER'



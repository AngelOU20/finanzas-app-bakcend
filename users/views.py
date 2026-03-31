from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .schemas import register_user_schema
from .serializers import UserRegistrationSerializer
from .services import create_user
from .types import UserCreateDTO


class UserRegistrationView(APIView):
  """
  Vista para el registro de nuevos usuarios. Permite crear un nuevo usuario proporcionando un nombre de usuario, correo electrónico, contraseña y rol. La vista valida los datos de entrada utilizando un serializer, luego empaqueta los datos limpios en un DTO estricto y ejecuta la lógica de negocio para crear el usuario. Finalmente, devuelve una respuesta con un mensaje de éxito y los detalles del usuario creado.
  """

  @register_user_schema
  def post(self, request):
    # Validar los datos de entrada utilizando el serializer
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Empaquetar los datos limpios en un DTO estricto 
    user_data = UserCreateDTO(**serializer.validated_data)
    
    # Ejecutar la lógica de negocio para crear el usuario 
    user = create_user(data=user_data)
    
    # Devolver una respuesta con un mensaje de éxito y los detalles del usuario creado
    return Response(
        {
            "mensaje": "Usuario creado con éxito",
            "usuario": {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role
            }
        },
        status=status.HTTP_201_CREATED
    )
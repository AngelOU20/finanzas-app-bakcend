from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .schemas import (
    change_password_schema,
    login_user_schema,
    logout_user_schema,
    me_schema,
    register_user_schema,
)
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    MeResponseSerializer,
    RegisterResponseSerializer,
    UserRegistrationSerializer,
)
from .services import change_password, create_user, logout_user
from .types import ChangePasswordDTO, UserCreateDTO


class UserRegistrationView(APIView):
    """
    Vista para el registro de nuevos usuarios. Permite crear un nuevo usuario proporcionando un nombre de usuario, correo electrónico, contraseña y rol. La vista valida los datos de entrada utilizando un serializer, luego empaqueta los datos limpios en un DTO estricto y ejecuta la lógica de negocio para crear el usuario. Finalmente, devuelve una respuesta con un mensaje de éxito y los detalles del usuario creado.
    """

    # Limita la creación de cuentas a 10 por hora por IP para evitar spam de registros
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register_attempts"

    @register_user_schema
    def post(self, request):
        # Validar los datos de entrada utilizando el serializer
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Empaquetar los datos limpios en un DTO estricto
        user_dto = UserCreateDTO(**serializer.validated_data)

        # Ejecutar la lógica de negocio para crear el usuario
        user = create_user(data=user_dto)

        # Devolver una respuesta con un mensaje de éxito y los detalles del usuario creado
        return Response(
            RegisterResponseSerializer(
                {
                    "message": "Usuario creado con éxito",
                    "user": user,
                }
            ).data,
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista para iniciar sesión y obtener tokens JWT. Esta vista utiliza un serializer personalizado para validar las credenciales del usuario y generar una respuesta que incluye los tokens de acceso y actualización, así como información adicional del usuario. Es la vista que se utiliza para el endpoint de login.
    """

    serializer_class = CustomTokenObtainPairSerializer

    # Configura el throttling para limitar los intentos de inicio de sesión a 5 por minuto por dirección IP
    throttle_classes = [ScopedRateThrottle]

    throttle_scope = "login_attempts"

    @login_user_schema
    def post(self, request, *args, **kwargs):
        # super().post se encargará de validar las credenciales, generar los tokens y devolver la respuesta personalizada definida en CustomTokenObtainPairSerializer
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["Autenticación"], summary="Refrescar Token de Acceso")
class CustomTokenRefreshView(TokenRefreshView):
    """
    Vista para refrescar el token de acceso utilizando un token de actualización válido. Esta vista se utiliza para obtener un nuevo token de acceso cuando el token actual ha expirado, siempre y cuando el token de actualización siga siendo válido. Es la vista que se utiliza para el endpoint de refresh.
    """

    pass


class LogoutView(APIView):
    """
    Vista para cerrar sesión. Esta vista recibe un Refresh Token válido y lo invalida agregándolo a la lista negra, lo que impide su uso futuro para obtener nuevos tokens de acceso. Requiere que el usuario esté autenticado para poder cerrar sesión.
    """

    permission_classes = [IsAuthenticated]

    @logout_user_schema
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            logout_user(serializer.validated_data["refresh"])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (TokenError, InvalidToken):
            return Response(
                {"error": "Token inválido o ya ha sido cerrado"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeView(APIView):
    """
    Vista para obtener los datos del usuario autenticado. Útil para que el
    frontend pueda recuperar la identidad del usuario tras un refresh de página
    cuando solo conserva el access token.
    """

    permission_classes = [IsAuthenticated]

    @me_schema
    def get(self, request):
        return Response(MeResponseSerializer(request.user).data)


class ChangePasswordView(APIView):
    """
    Vista para que un usuario autenticado cambie su contraseña.
    Valida la contraseña actual y los validadores de Django sobre la nueva.
    """

    permission_classes = [IsAuthenticated]

    @change_password_schema
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        change_password(
            data=ChangePasswordDTO(
                user=request.user,
                new_password=serializer.validated_data["new_password"],
            )
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

import pytest
from django.urls import reverse_lazy
from rest_framework import status

from users.factories import UserFactory
from users.models import User


@pytest.mark.django_db
class TestUserRegistration:
    """Tests para el endpoint de registro de nuevos usuarios."""

    url = reverse_lazy("register_user")

    def test_successful_user_registration(self, api_client):
        """
        Happy path: payload válido y completo debe crear el usuario y retornar 201.
        """

        payload = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "password": "SecurePassword123",
            "password_confirm": "SecurePassword123",
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.count() == 1
        assert User.objects.first().email == "johndoe@example.com"
        assert User.objects.first().role == User.Role.USER

    def test_registration_fails_with_missing_fields(self, api_client):
        """
        El serializer debe rechazar un payload sin email, que es campo obligatorio.
        """

        payload = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePassword123",
            "password_confirm": "SecurePassword123",
            "role": User.Role.USER,
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.count() == 0

    def test_registration_fails_with_mismatched_passwords(self, api_client):
        """
        El serializer debe rechazar el registro si las contraseñas no coinciden.
        """

        payload = {
            "username": "hacker",
            "email": "hacker@example.com",
            "password": "C0mplexP@ssword!",
            "password_confirm": "C0mplexP@ssword!_different",
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Verificamos que el error apunta al campo correcto, no a otro cualquiera
        assert "password_confirm" in response.data
        assert User.objects.count() == 0

    def test_registration_fails_with_duplicate_email(self, api_client):
        """
        El serializer debe rechazar el registro si el email ya existe en la bd.
        """

        existing_user = UserFactory(email="existing@example.com")

        payload = {
            "username": "johndoe",
            "email": existing_user.email,  # Intentamos registrar con un email que ya existe
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePassword123",
            "password_confirm": "SecurePassword123",
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.count() == 1


@pytest.mark.django_db
class TestUserLogin:
    """
    Tests para el endpoint de autenticación (obtención de tokens JWT).
    """

    url = reverse_lazy("token_obtain_pair")

    def test_successful_login_returns_tokens(self, api_client, raw_password):
        """
        Login con credenciales válidas debe retornar tokens de acceso y refresco.
        Usamos la factory porque el usuario debe preexistir en la BD antes del login.
        """
        user = UserFactory(password=raw_password)
        payload = {
            "username": user.username,
            "password": raw_password,
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["username"] == user.username

    def test_login_fails_with_invalid_credentials(self, api_client, raw_password):
        """
        Login con credenciales incorrectas debe retornar error 401 y mensaje genérico.
        """

        user = UserFactory(password=raw_password)
        payload = {
            "username": user.username,
            "password": "WrongPassword!",
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data
        assert "refresh" not in response.data
        assert (
            response.data["detail"]
            == "Credenciales incorrectas o la cuenta está inactiva."
        )


@pytest.mark.django_db
class TestLogout:
    """
    Tests para el endpoint de logout, que agregue el token de refresh a la lista negra.
    """

    url = reverse_lazy("logout")

    def test_successful_logout_blacklists_token(self, api_client, raw_password):
        """
        Logout con refresh token válido debe invalidarlo (blacklist) y retornar 204.
        El token no debe poder usarse nuevamente después del logout.
        """

        user = UserFactory(password=raw_password)

        # Primero hacemos login para obtener un refresh token real
        login_response = api_client.post(
            reverse_lazy("token_obtain_pair"),
            {"username": user.username, "password": raw_password},
            format="json",
        )
        refresh_token = login_response.data["refresh"]
        access_token = login_response.data["access"]

        # Autenticamos el cliente con el access token (el endpoint requiere IsAuthenticated)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = api_client.post(
            self.url,
            {"refresh": refresh_token},
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_fails_with_invalid_token(self, api_client, raw_password):
        """
        Logout con un token inválido debe retornar 400 y no afectar a la base de datos.
        """

        user = UserFactory(password=raw_password)

        login_response = api_client.post(
            reverse_lazy("token_obtain_pair"),
            {
                "username": user.username,
                "password": raw_password,
            },
            format="json",
        )

        access_token = login_response.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = api_client.post(
            self.url,
            {"refresh": "esto.no.es.un.token.valido"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Token inválido o ya ha sido cerrado"

    def test_logout_fails_without_authentication(self, api_client, raw_password):
        """
        El endpoint requiere IsAuthenticated. Sin header Authorization debe retornar 401.
        Verifica que permission_classes está correctamente configurado.
        """
        user = UserFactory(password=raw_password)

        login_response = api_client.post(
            reverse_lazy("token_obtain_pair"),
            {"username": user.username, "password": raw_password},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        # No se configuran credenciales — cliente anónimo
        response = api_client.post(
            self.url,
            {"refresh": refresh_token},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_fails_with_already_used_token(self, api_client, raw_password):
        """
        Un refresh token que ya fue usado para logout no debe poder usarse de nuevo.
        Esto verifica que el blacklist realmente funciona.
        """

        user = UserFactory(password=raw_password)

        login_response = api_client.post(
            reverse_lazy("token_obtain_pair"),
            {"username": user.username, "password": raw_password},
            format="json",
        )
        refresh_token = login_response.data["refresh"]
        access_token = login_response.data["access"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Primer logout — debe funcionar
        api_client.post(self.url, {"refresh": refresh_token}, format="json")

        # Segundo logout con el mismo token — debe fallar
        second_response = api_client.post(
            self.url,
            {"refresh": refresh_token},
            format="json",
        )

        assert second_response.status_code == status.HTTP_400_BAD_REQUEST
        assert second_response.data["error"] == "Token inválido o ya ha sido cerrado"


@pytest.mark.django_db
class TestTokenRefresh:
    """
    Tests para el endpoint de refresco de token de acceso.
    """

    url = reverse_lazy("token_refresh")

    def test_successful_token_refresh(self, api_client, raw_password):
        """
        Un refresh token válido debe generar un nuevo access token.
        Verifica el flujo normal de renovación silenciosa de sesión.
        """
        user = UserFactory(password=raw_password)

        login_response = api_client.post(
            reverse_lazy("token_obtain_pair"),
            {"username": user.username, "password": raw_password},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        response = api_client.post(
            self.url,
            {"refresh": refresh_token},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        # El nuevo access token debe ser diferente al original
        assert response.data["access"] != login_response.data["access"]

    def test_refresh_fails_with_invalid_token(self, api_client):
        """
        Un refresh token inválido o malformado debe retornar 401.
        """

        response = api_client.post(
            self.url,
            {"refresh": "token.completamente.falso"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data

    def test_refresh_fails_after_logout(self, api_client, raw_password):
        """
        Un refresh token que fue invalidado por logout no debe poder generar nuevos access tokens.
        Este test conecta el sistema de blacklist con el de refresh — verifica que ambos trabajan juntos.
        """

        user = UserFactory(password=raw_password)

        login_response = api_client.post(
            reverse_lazy("token_obtain_pair"),
            {"username": user.username, "password": raw_password},
            format="json",
        )
        refresh_token = login_response.data["refresh"]
        access_token = login_response.data["access"]

        # Hacemos logout para blacklistear el refresh token
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        api_client.post(
            reverse_lazy("logout"),
            {"refresh": refresh_token},
            format="json",
        )
        api_client.credentials()  # Limpiamos credenciales

        # Intentamos usar el refresh token blacklisteado
        response = api_client.post(
            self.url,
            {"refresh": refresh_token},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

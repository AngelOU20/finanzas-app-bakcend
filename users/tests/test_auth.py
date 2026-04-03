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
            "role": User.Role.USER,
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.count() == 1
        assert User.objects.first().email == "johndoe@example.com"

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
            "password": "Password123",
            "password_confirm": "DifferentPassword",
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Verificamos que el error apunta al campo correcto, no a otro cualquiera
        assert "password_confirm" in response.data
        assert User.objects.count() == 0


@pytest.mark.django_db
class TestUserLogin:
    """
    Tests para el endpoint de autenticación (obtención de tokens JWT).
    """

    url = reverse_lazy("token_obtain_pair")
    # Constante compartida para evitar que el string esté duplicado
    # y se desincronice si alguien lo cambia en un lugar y olvida el otro.
    RAW_PASSWORD = "KnownPassword123!"

    def test_successful_login_returns_tokens(self, api_client):
        """
        Login con credenciales válidas debe retornar tokens de acceso y refresco.
        Usamos la factory porque el usuario debe preexistir en la BD antes del login.
        """
        user = UserFactory(password=self.RAW_PASSWORD)
        payload = {
            "username": user.username,
            "password": self.RAW_PASSWORD,
        }

        response = api_client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["username"] == user.username

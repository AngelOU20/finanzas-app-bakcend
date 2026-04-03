import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """
    Fixture global que simula un cliente HTTP para realizar solicitudes a la API durante las pruebas. Proporciona una instancia de APIClient que se puede usar en cualquier prueba para enviar solicitudes a los endpoints de la aplicación. Esto permite probar la funcionalidad de la API de manera aislada y controlada.
    """
    return APIClient()

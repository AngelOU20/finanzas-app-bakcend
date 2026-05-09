import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """
    Fixture global que simula un cliente HTTP para realizar solicitudes a la API durante las pruebas. Proporciona una instancia de APIClient que se puede usar en cualquier prueba para enviar solicitudes a los endpoints de la aplicación. Esto permite probar la funcionalidad de la API de manera aislada y controlada.
    """
    return APIClient()


@pytest.fixture
def raw_password():
    """
    Fixture global que proporciona una contraseña conocida y constante para usar en las pruebas de autenticación. Esto asegura que todas las pruebas que requieren una contraseña utilicen el mismo valor, evitando inconsistencias y facilitando la gestión de las credenciales de prueba.
    """
    return "KnownPassword123!"


@pytest.fixture(autouse=True)
def disable_throttling(settings):
    """
    Eleva los límites de throttling a valores que nunca se alcanzan en tests.

    Vaciar DEFAULT_THROTTLE_CLASSES no es suficiente porque CustomTokenObtainPairView
    define throttle_classes = [ScopedRateThrottle] a nivel de vista, lo que bypasea
    el setting global. La solución correcta es mantener las clases intactas y
    sobreescribir solo los rates para que nunca se dispare el límite durante los tests.
    """
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
        "anon": "10000/min",
        "user": "10000/min",
        "login_attempts": "10000/min",
        "register_attempts": "10000/min",
    }

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView


urlpatterns = [
    # Ruta para registrarse: http://127.0.0.1:8000/api/users/register/
    path('register/', UserRegistrationView.as_view(), name='register_user'),
    
    # Rutas para el Login con JWT
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
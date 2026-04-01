from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    UserRegistrationView,
)

urlpatterns = [
    # Rutas para el registro y logout de usuarios
    path("register/", UserRegistrationView.as_view(), name="register_user"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Rutas para el Login con JWT
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]

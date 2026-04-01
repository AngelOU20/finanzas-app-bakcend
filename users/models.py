from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo de usuario personalizado que extiende el usuario de Django AbstractUser. Agrega campos adicionales como email y role para diferenciar entre usuarios normales y administradores.
    """

    # Definimos las opciones de rol utilizando TextChoices para facilitar la selección de roles en el modelo
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        USER = "USER", "Usuario"

    # Agregamos nuestros campos personalizados
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    # Sobrescribimos el método __str__ para mostrar el nombre de usuario y el rol
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

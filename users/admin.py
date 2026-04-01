from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active")
    # Añadimos el campo role a los formularios de edición
    fieldsets = UserAdmin.fieldsets + (("Extra Info", {"fields": ("role",)}),)
    # Añadimos el campo role al formulario de creación
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Info", {"fields": ("role", "email")}),
    )

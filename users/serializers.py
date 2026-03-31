from rest_framework import serializers
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
  """
  Serializer para el registro de usuarios. Permite crear un nuevo usuario con un nombre de usuario, correo electrónico, contraseña y rol. La contraseña se marca como write_only para que no se devuelva en las respuestas.
  """
  password = serializers.CharField(write_only=True, style={'input_type': 'password'})
  password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'}, label='Confirmar Contraseña')

  class Meta:
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password_confirm', 'role']

  def validate(self, attrs):
    """
    Validación personalizada para asegurar que las contraseñas coincidan. Si las contraseñas no coinciden, se lanza un error de validación.
    """
    # Extraemos el campo password
    password = attrs.get('password')
    # Extraemos el campo password_confirm para compararlo con password, pero lo eliminamos de attrs para que no se intente guardar en el modelo
    password_confirm = attrs.pop('password_confirm', None)  
    
    if password != password_confirm:
      # Si las contraseñas no coinciden, lanzamos un error de validación con un mensaje específico
      raise serializers.ValidationError(
        {"password_confirm": "Las contraseñas no coinciden."}
      )
    
    return attrs

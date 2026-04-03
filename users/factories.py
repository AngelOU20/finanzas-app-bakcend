import factory

from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = User.Role.USER

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        # extracted es el valor pasado como argumento, si no se pasa usa el default
        raw_password = extracted or "TestPassword123!"
        self.set_password(raw_password)
        if create:
            self.save()  # Save explícito y controlado

import factory
from faker import Faker
from api.models import User

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: fake.user_name())
    email = factory.LazyAttribute(lambda _: fake.email())
    is_staff = False
    is_superuser = False

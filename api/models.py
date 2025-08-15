from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
# models.py
from django.contrib.auth.models import User
from django.db import models

User = get_user_model()

#Relationshipe made for the users
User.add_to_class(
    "following",
    models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True
    )
)

# receitas

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ingredients = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Ingredients(model.Model):
    name = models.TextField()
    
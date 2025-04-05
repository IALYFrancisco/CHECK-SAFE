from django.db import models
# Create your models here.
from django.contrib.auth.models import User  # Utilise le modèle User de Django pour la gestion des utilisateurs

class UserAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Relation un à un avec le modèle User
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.street_address}, {self.city}, {self.country}, {self.postal_code}"


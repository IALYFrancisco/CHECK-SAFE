from django.db import models

# Create your models here.

class Transaction(models.Model):
    client_id = models.CharField(max_length=100)
    date = models.DateTimeField()
    montant = models.FloatField()
    type_transaction = models.CharField(max_length=50)
    is_fraudulent = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction {self.id} - Client {self.client_id}"

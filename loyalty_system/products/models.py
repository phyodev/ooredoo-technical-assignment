from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    points_earned = models.IntegerField(default=0)  # Points customer earns per purchase

    def __str__(self):
        return self.name

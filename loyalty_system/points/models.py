from django.db import models
from users.models import CustomUser
from datetime import timedelta, date

class PointLedger(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = date.today() + timedelta(days=365)  # Points expire in 1 year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.username} - {self.points} points"

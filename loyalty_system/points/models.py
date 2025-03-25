from django.db import models
from django.utils import timezone
from django.conf import settings
from users.models import CustomUser
from datetime import timedelta, date

class PointLedger(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = date.today() + timedelta(days=settings.POINTS_EXPIRY)  # Points expire in 1 year
        super().save(*args, **kwargs)
    
    @staticmethod
    def get_available_points(customer):
        """
        Calculate the total non-expired points a customer has.
        """
        now = timezone.now()
        total_points = PointLedger.objects.filter(
            customer=customer, expires_at__gt=now
        ).aggregate(total=models.Sum('points'))['total']
        return total_points or 0

    def __str__(self):
        return f"{self.customer.username} - {self.points} points"

class Redemption(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    customer = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.product.name} ({self.status})"

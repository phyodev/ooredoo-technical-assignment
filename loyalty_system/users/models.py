from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from points.models import PointLedger

class CustomUser(AbstractUser):  
    TIER_CHOICES = [
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ]
    
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='Silver')
    total_points = models.IntegerField(default=0)

    def upgrade_tier(self):
        # Update total_points before upgrading tier
        self.total_points = PointLedger.get_available_points(self)

        # Check if the user qualifies for a tier upgrade
        if self.total_points >= settings.GOLD_TIER['MINIMUM_POINTS'] and \
            self.total_points < settings.PLATINUM_TIER['MINIMUM_POINTS']:
            self.tier = 'Gold'
        elif self.total_points >= settings.PLATINUM_TIER['MINIMUM_POINTS']:
            self.tier = 'Platinum'
        else:
            self.tier = 'Silver'

        self.save()
    def __str__(self):
        return f"{self.username} - {self.tier}"

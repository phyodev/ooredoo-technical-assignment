from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):  
    TIER_CHOICES = [
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ]
    
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='Silver')
    total_points = models.IntegerField(default=0)

    def upgrade_tier(self):
        if self.total_points >= settings.GOLD_TIER['MINIMUM_POINTS']:
            self.tier = 'Gold'
        if self.total_points >= settings.PLATINUM_TIER['MINIMUM_POINTS']:
            self.tier = 'Platinum'
        self.save()

    def __str__(self):
        return f"{self.username} - {self.tier}"

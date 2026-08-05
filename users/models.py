from django.contrib.auth.models import AbstractUser
from django.db import models
import random


def generate_random_mobile():
    return "9" + "".join(random.choices("0123456789", k=9))

class CustomUser(AbstractUser):
    STATUS_CHOICES = (
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('DENIED', 'DENIED'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    mobile = models.CharField(max_length=10, default=generate_random_mobile, blank=True)


class UserOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


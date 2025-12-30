from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random
# Create your models here.
class User(AbstractUser):
        email = models.EmailField(unique=True)
        USERNAME_FIELD = 'email'

        REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

        def __str__(self):
                return self.username

class OTP(models.Model):
        email = models.EmailField()
        otp = models.CharField(max_length=4)
        created_at = models.DateTimeField(auto_now_add=True)
        is_used = models.BooleanField(default=False)

#function to validate the token if it was used 
        def is_valid(self):
                return not self.is_used and timezone.now() < self.created_at + timedelta(minutes=10)

        @staticmethod
        def generate_otp():
                return str(random.randint(1000, 9999))
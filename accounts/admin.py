from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import OTP

# Register your models here.

User = get_user_model() # storing model to variable for easy access

admin.site.register(User, UserAdmin)
admin.site.register(OTP)

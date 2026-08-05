from django.contrib import admin

from .models import CustomUser, UserOTP

admin.site.register(CustomUser)
admin.site.register(UserOTP)

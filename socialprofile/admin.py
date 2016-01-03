"""Django Admin Site configuration for socialprofiles"""

# pylint: disable=R0901,R0904

from django.contrib import admin
from . import models

class CustomUserAdmin(admin.ModelAdmin):
    """Sets up the custom user admin display"""
    list_display = ('username', 'email', 'gender', 'first_name', 'last_name', 'is_staff', 'is_active', 'manually_edited')

admin.site.register(models.SocialProfile, CustomUserAdmin)

"""Django Admin Site configuration for socialprofiles"""

# pylint: disable=R0901,R0904

from django.contrib import admin
from socialprofile.models import SocialProfile
from image_cropping.admin import ImageCroppingMixin

class CustomUserAdmin(ImageCroppingMixin, admin.ModelAdmin):
    """Sets up the custom user admin display"""
    list_display = ('username', 'email', 'gender', 'first_name', 'last_name', 'is_staff', 'is_active', 'manually_edited','visible')

admin.site.register(SocialProfile, CustomUserAdmin)

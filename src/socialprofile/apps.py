"""Django App configuration for socialprofile"""

from django.apps import AppConfig


class SocialProfileConfig(AppConfig):
    """Default configuration for socialprofile"""

    default_auto_field = "django.db.models.AutoField"
    name = "socialprofile"
    verbose_name = "Social Profile"

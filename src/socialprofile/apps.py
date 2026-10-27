"""Django App configuration for socialprofile"""

from django.apps import AppConfig


class SocialProfileConfig(AppConfig):
    """Default configuration for socialprofile"""

    default_auto_field = "django.db.models.AutoField"
    name = "socialprofile"
    verbose_name = "Social Profile"

    def ready(self) -> None:
        from socialprofile.rbac import connect_rbac_signals

        connect_rbac_signals()

"""Django Admin Site configuration for socialprofiles"""

# pylint: disable=R0901,R0904

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from image_cropping.admin import ImageCroppingMixin
from social_django.admin import AssociationOption, NonceOption, UserSocialAuthOption
from social_django.models import Association, Nonce, UserSocialAuth

from socialprofile.models import SocialProfile


@admin.register(SocialProfile)
class CustomUserAdmin(ImageCroppingMixin, BaseUserAdmin):
    """Sets up the custom user admin display"""

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone_number")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined", "date_of_birth")},
        ),
        (_("Common Info"), {"fields": ("country", "gender", "url", "image_url")}),
        (
            _("Staff"),
            {
                "fields": (
                    "sort",
                    "visible",
                    "title",
                    "role",
                    "function_01",
                    "function_02",
                    "function_03",
                    "function_04",
                    "function_05",
                    "function_06",
                    "function_07",
                    "function_08",
                    "function_09",
                    "function_10",
                )
            },
        ),
        (_("Providers"), {"fields": ("edited_by_user", "edited_by_provider")}),
        (
            "Google",
            {
                "fields": (
                    "google_username",
                    "google_isPlusUser",
                    "google_url",
                    "google_circledByCount",
                    "google_language",
                    "google_kind",
                    "google_verified",
                )
            },
        ),
        (
            "Twitter",
            {
                "fields": (
                    "twitter_username",
                    "twitter_url",
                    "twitter_language",
                    "twitter_verified",
                )
            },
        ),
        ("Facebook", {"fields": ("facebook_username", "facebook_url")}),
        ("Instagram", {"fields": ("instagram_username", "instagram_url")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "email", "password1", "password2"),
            },
        ),
    )
    readonly_fields = [
        "email",
        "last_login",
        "date_joined",
        "edited_by_user",
        "edited_by_provider",
        "google_isPlusUser",
        "google_circledByCount",
        "google_language",
        "google_kind",
        "google_verified",
        "twitter_language",
        "twitter_verified",
    ]
    # form = UserChangeForm
    # add_form = UserCreationForm
    list_display = (
        "email",
        "username",
        "gender",
        "first_name",
        "last_name",
        "is_active",
        "edited_by_user",
        "edited_by_provider",
        "visible",
        "date_joined",
        "last_login",
    )
    search_fields = ("email", "first_name", "last_name", "groups", "user_permissions")

    ordering = (
        "last_login",
        "date_joined",
        "email",
    )


class ProxyUserSocialAuth(UserSocialAuth):
    """Create UserSocialAuth proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = "OAuth: " + str(UserSocialAuth._meta.verbose_name)
        verbose_name_plural = "OAuth: " + str(UserSocialAuth._meta.verbose_name_plural)


class ProxyNonce(Nonce):
    """Create Nonce proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = "OAuth: " + str(Nonce._meta.verbose_name)
        verbose_name_plural = "OAuth: " + str(Nonce._meta.verbose_name_plural)


class ProxyAssociation(Association):
    """Create Association proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = "OAuth: " + str(Association._meta.verbose_name)
        verbose_name_plural = "OAuth: " + str(Association._meta.verbose_name_plural)


admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)
admin.site.register(ProxyUserSocialAuth, UserSocialAuthOption)
admin.site.register(ProxyNonce, NonceOption)
admin.site.register(ProxyAssociation, AssociationOption)

from django_otp.plugins.otp_static.admin import StaticDeviceAdmin
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice
from two_factor.admin import PhoneDeviceAdmin
from two_factor.models import PhoneDevice


class ProxyPhoneDevice(PhoneDevice):
    """Create PhoneDevice proxy model for OAuth two_factor"""

    class Meta:
        proxy = True
        verbose_name = "Otp: " + str(PhoneDevice._meta.verbose_name)
        verbose_name_plural = "Otp: " + str(PhoneDevice._meta.verbose_name_plural)


class ProxyStaticDevice(StaticDevice):
    """Create StaticDevice proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = "Otp: " + str(StaticDevice._meta.verbose_name)
        verbose_name_plural = "Otp: " + str(StaticDevice._meta.verbose_name_plural)


class ProxyTOTPDevice(TOTPDevice):
    """Create TOTPDevice proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = "Otp: " + str(TOTPDevice._meta.verbose_name)
        verbose_name_plural = "Otp: " + str(TOTPDevice._meta.verbose_name_plural)


admin.site.unregister(PhoneDevice)
admin.site.unregister(StaticDevice)
admin.site.unregister(TOTPDevice)
admin.site.register(ProxyPhoneDevice, PhoneDeviceAdmin)
admin.site.register(ProxyStaticDevice, StaticDeviceAdmin)
admin.site.register(ProxyTOTPDevice, TOTPDeviceAdmin)

from user_sessions.admin import SessionAdmin
from user_sessions.models import Session


class ProxySession(Session):
    """Create Session proxy model for user_session"""

    class Meta:
        proxy = True
        verbose_name = "Monitor: " + str(Session._meta.verbose_name)
        verbose_name_plural = "Monitor: " + str(Session._meta.verbose_name_plural)


admin.site.unregister(Session)
admin.site.register(ProxySession, SessionAdmin)

from axes.admin import AccessAttemptAdmin, AccessLogAdmin
from axes.models import AccessAttempt, AccessLog


class ProxyAccessAttempt(AccessAttempt):
    """Create AccessAttempt proxy model for user_session"""

    class Meta:
        proxy = True
        verbose_name = "Monitor: " + str(AccessAttempt._meta.verbose_name)
        verbose_name_plural = "Monitor: " + str(AccessAttempt._meta.verbose_name_plural)


class ProxyAccessLog(AccessLog):
    """Create Axes proxy model for user_session"""

    class Meta:
        proxy = True
        verbose_name = "Monitor: " + str(AccessLog._meta.verbose_name)
        verbose_name_plural = "Monitor: " + str(AccessLog._meta.verbose_name_plural)


admin.site.unregister(AccessAttempt)
admin.site.unregister(AccessLog)
admin.site.register(ProxyAccessAttempt, AccessAttemptAdmin)
admin.site.register(ProxyAccessLog, AccessLogAdmin)

from oauth2_provider.admin import (
    AccessTokenAdmin,
    ApplicationAdmin,
    GrantAdmin,
    RefreshTokenAdmin,
)
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model,
    get_grant_model,
    get_refresh_token_model,
)

Application = get_application_model()
Grant = get_grant_model()
AccessToken = get_access_token_model()
RefreshToken = get_refresh_token_model()


class ProxyApplication(Application):
    """Create Application proxy model for user_session"""

    class Meta:
        proxy = True
        verbose_name = "Token: " + str(Application._meta.verbose_name)
        verbose_name_plural = "Token: " + str(Application._meta.verbose_name_plural)


class ProxyGrant(Grant):
    """Create Grant proxy model for user_session"""

    class Meta:
        proxy = True
        verbose_name = "Token: " + str(Grant._meta.verbose_name)
        verbose_name_plural = "Token: " + str(Grant._meta.verbose_name_plural)


class ProxyAccessToken(AccessToken):
    """Create AccessToken proxy model for user_session"""

    class Meta:
        proxy = True
        verbose_name = "Token: " + str(AccessToken._meta.verbose_name)
        verbose_name_plural = "Token: " + str(AccessToken._meta.verbose_name_plural)


class ProxyRefreshToken(RefreshToken):
    """Create RefreshToken proxy model for user_session"""

    class Meta:
        proxy = True
        verbose_name = f"Token: {RefreshToken._meta.verbose_name}"
        verbose_name_plural = f"Token: {RefreshToken._meta.verbose_name_plural}"


admin.site.unregister(
    Application,
)
admin.site.unregister(Grant)
admin.site.unregister(AccessToken)
admin.site.unregister(RefreshToken)
admin.site.register(ProxyApplication, ApplicationAdmin)
admin.site.register(ProxyGrant, GrantAdmin)
admin.site.register(ProxyAccessToken, AccessTokenAdmin)
admin.site.register(ProxyRefreshToken, RefreshTokenAdmin)

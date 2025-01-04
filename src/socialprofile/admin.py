"""Django Admin Site configuration for socialprofiles"""

from axes.admin import AccessAttemptAdmin, AccessLogAdmin
from axes.models import AccessAttempt, AccessLog
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django_otp.plugins.otp_static.admin import StaticDeviceAdmin
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice
from image_cropping.admin import ImageCroppingMixin
from oauth2_provider.admin import (
    AccessTokenAdmin,
    ApplicationAdmin,
    GrantAdmin,
    IDTokenAdmin,
    RefreshTokenAdmin,
)
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model,
    get_grant_model,
    get_id_token_model,
    get_refresh_token_model,
)
from social_django.admin import AssociationOption, NonceOption, UserSocialAuthOption
from social_django.models import Association, Nonce, UserSocialAuth
from user_sessions.admin import SessionAdmin
from user_sessions.models import Session

from socialprofile.models import SocialProfile

# from rest_framework.authtoken.admin import TokenAdmin
# from rest_framework.authtoken.models import Token, TokenProxy


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
            _("Avatar"),
            {
                "fields": (
                    "image",
                    "cropping",
                    "cropping_free",
                )
            },
        ),
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
        (
            _("Providers"),
            {
                "fields": (
                    "edited_by_user",
                    "edited_by_google",
                    "edited_by_twitter",
                    "edited_by_facebook",
                    "edited_by_instagram",
                    "edited_by_live",
                )
            },
        ),
        (
            "Google",
            {
                "fields": (
                    "google_username",
                    "google_email",
                    "google_isPlusUser",
                    "google_url",
                    "google_circledByCount",
                    "google_language",
                    "google_kind",
                    "google_verified",
                    "google_avatar",
                )
            },
        ),
        (
            "Twitter",
            {
                "fields": (
                    "twitter_username",
                    "twitter_email",
                    "twitter_url",
                    "twitter_language",
                    "twitter_verified",
                    "twitter_avatar",
                )
            },
        ),
        (
            "Facebook",
            {
                "fields": (
                    "facebook_username",
                    "facebook_email",
                    "facebook_url",
                    "facebook_avatar",
                )
            },
        ),
        (
            "Instagram",
            {
                "fields": (
                    "instagram_username",
                    "instagram_email",
                    "instagram_url",
                    "instagram_avatar",
                )
            },
        ),
        (
            "Live",
            {
                "fields": (
                    "live_username",
                    "live_email",
                    "live_url",
                    "live_language",
                    "live_avatar",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    readonly_fields = [
        # "email",
        "last_login",
        "date_joined",
        "edited_by_user",
        "edited_by_google",
        "edited_by_twitter",
        "edited_by_facebook",
        "edited_by_instagram",
        "edited_by_live",
        "google_username",
        "google_isPlusUser",
        "google_url",
        "google_circledByCount",
        "google_language",
        "google_kind",
        "google_verified",
        "google_avatar",
        "twitter_username",
        "twitter_url",
        "twitter_language",
        "twitter_verified",
        "twitter_avatar",
        "facebook_username",
        "facebook_url",
        "facebook_avatar",
        "instagram_username",
        "instagram_url",
        "instagram_avatar",
        "live_username",
        "live_url",
        "live_language",
        "live_avatar",
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
        "edited_by_google",
        "edited_by_twitter",
        "edited_by_facebook",
        "edited_by_instagram",
        "edited_by_live",
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


# social_django
class ProxyUserSocialAuth(UserSocialAuth):
    """Create UserSocialAuth proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = f"OAuth: {UserSocialAuth._meta.verbose_name}"
        verbose_name_plural = f"OAuth: {UserSocialAuth._meta.verbose_name_plural}"


class ProxyNonce(Nonce):
    """Create Nonce proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = f"OAuth: {Nonce._meta.verbose_name}"
        verbose_name_plural = f"OAuth: {Nonce._meta.verbose_name_plural}"


class ProxyAssociation(Association):
    """Create Association proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = f"OAuth: {Association._meta.verbose_name}"
        verbose_name_plural = f"OAuth: {Association._meta.verbose_name_plural}"


admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)
admin.site.register(ProxyUserSocialAuth, UserSocialAuthOption)
admin.site.register(ProxyNonce, NonceOption)
admin.site.register(ProxyAssociation, AssociationOption)


# rest_framework
# class ProxyTokenAdmin(TokenProxy):
#     """Create TokenProxy proxy model for rest_framework"""
#
#     class Meta:
#         proxy = True
#         verbose_name = f"Rest Framework: {TokenProxy._meta.verbose_name}"
#         verbose_name_plural = f"Rest Framework: {TokenProxy._meta.verbose_name_plural}"
#
#
# admin.site.unregister(TokenProxy)
# admin.site.register(TokenProxy, ProxyTokenAdmin)


# django_otp
class ProxyStaticDevice(StaticDevice):
    """Create StaticDevice proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = f"Otp: {StaticDevice._meta.verbose_name}"
        verbose_name_plural = f"Otp: {StaticDevice._meta.verbose_name_plural}"


class ProxyTOTPDevice(TOTPDevice):
    """Create TOTPDevice proxy model for OAuth social_django"""

    class Meta:
        proxy = True
        verbose_name = f"Otp: {TOTPDevice._meta.verbose_name}"
        verbose_name_plural = f"Otp: {TOTPDevice._meta.verbose_name_plural}"


admin.site.unregister(StaticDevice)
admin.site.unregister(TOTPDevice)
admin.site.register(ProxyStaticDevice, StaticDeviceAdmin)
admin.site.register(ProxyTOTPDevice, TOTPDeviceAdmin)


# user_sessions
class ProxySession(Session):
    """Create Session proxy model for user_session"""

    class Meta:
        proxy = True
        verbose_name = f"Monitor: {Session._meta.verbose_name}"
        verbose_name_plural = f"Monitor: {Session._meta.verbose_name_plural}"


admin.site.unregister(Session)
admin.site.register(ProxySession, SessionAdmin)


# axes
class ProxyAccessAttempt(AccessAttempt):
    """Create AccessAttempt proxy model for axes"""

    class Meta:
        proxy = True
        verbose_name = f"Monitor: {AccessAttempt._meta.verbose_name}"
        verbose_name_plural = f"Monitor: {AccessAttempt._meta.verbose_name_plural}"


class ProxyAccessLog(AccessLog):
    """Create Axes proxy model for axes"""

    class Meta:
        proxy = True
        verbose_name = f"Monitor: {AccessLog._meta.verbose_name}"
        verbose_name_plural = f"Monitor: {AccessLog._meta.verbose_name_plural}"


admin.site.unregister(AccessAttempt)
admin.site.unregister(AccessLog)
admin.site.register(ProxyAccessAttempt, AccessAttemptAdmin)
admin.site.register(ProxyAccessLog, AccessLogAdmin)

# oauth2_provider
Application = get_application_model()
Grant = get_grant_model()
AccessToken = get_access_token_model()
RefreshToken = get_refresh_token_model()
IDToken = get_id_token_model()


class ProxyApplication(Application):
    """Create Application proxy model for oauth2_provider"""

    class Meta:
        proxy = True
        verbose_name = f"Token: {Application._meta.verbose_name}"
        verbose_name_plural = f"Token: {Application._meta.verbose_name_plural}"


class ProxyGrant(Grant):
    """Create Grant proxy model for oauth2_provider"""

    class Meta:
        proxy = True
        verbose_name = f"Token: {Grant._meta.verbose_name}"
        verbose_name_plural = f"Token: {Grant._meta.verbose_name_plural}"


class ProxyAccessToken(AccessToken):
    """Create AccessToken proxy model for oauth2_provider"""

    class Meta:
        proxy = True
        verbose_name = f"Token: {AccessToken._meta.verbose_name}"
        verbose_name_plural = f"Token: {AccessToken._meta.verbose_name_plural}"


class ProxyRefreshToken(RefreshToken):
    """Create RefreshToken proxy model for oauth2_provider"""

    class Meta:
        proxy = True
        verbose_name = f"Token: {RefreshToken._meta.verbose_name}"
        verbose_name_plural = f"Token: {RefreshToken._meta.verbose_name_plural}"


class ProxyIDToken(IDToken):
    """Create IDToken proxy model for oauth2_provider"""

    class Meta:
        proxy = True
        verbose_name = f"Token: {IDToken._meta.verbose_name}"
        verbose_name_plural = f"Token: {IDToken._meta.verbose_name_plural}"


admin.site.unregister(Application)
admin.site.unregister(Grant)
admin.site.unregister(AccessToken)
admin.site.unregister(RefreshToken)
admin.site.unregister(IDToken)
admin.site.register(ProxyApplication, ApplicationAdmin)
admin.site.register(ProxyGrant, GrantAdmin)
admin.site.register(ProxyAccessToken, AccessTokenAdmin)
admin.site.register(ProxyRefreshToken, RefreshTokenAdmin)
admin.site.register(ProxyIDToken, IDTokenAdmin)

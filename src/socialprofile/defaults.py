"""Package defaults for django-sp (socialprofile) consumer settings."""

DEFAULT_SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.mail.mail_validation",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "socialprofile.pipeline.socialprofile_extra_values",
)

# Not appended by apply_sp_defaults. Consumers set SP_PARTY_SYNC=True and append:
# "socialprofile.party_sync.sync_party_from_profile"
PARTY_SYNC_PIPELINE_STEP = "socialprofile.party_sync.sync_party_from_profile"

# Opt-in IdP backends (append to AUTHENTICATION_BACKENDS). No fat SocialProfile columns.
OPTIONAL_SOCIAL_AUTH_BACKENDS = (
    "social_core.backends.linkedin.LinkedinOAuth2",
    "social_core.backends.discord.DiscordOAuth2",
    "social_core.backends.github.GithubOAuth2",
)

DEFAULT_AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.email.EmailAuth",
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
)

DEFAULT_OAUTH2_PROVIDER = {
    "OAUTH2_VALIDATOR_CLASS": "socialprofile.validators.AxesOAuth2Validator",
}

DEFAULT_AXES_BEHIND_PROXY = {
    "AXES_LOCKOUT_PARAMETERS": ["ip_address"],
    "AXES_IPWARE_PROXY_COUNT": 1,
    "AXES_IPWARE_META_PRECEDENCE_ORDER": [
        "HTTP_X_FORWARDED_FOR",
        "REMOTE_ADDR",
    ],
}

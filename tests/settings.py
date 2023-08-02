"""Test's settings"""
DEBUG = False

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

SECRET_KEY = "NOTASECRET"

ALLOWED_HOSTS = ["*"]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "social_django.context_processors.backends",  # Need By SocialProfile
                "social_django.context_processors.login_redirect",  # Need By SocialProfile
            ],
        },
    },
]

ROOT_URLCONF = "socialprofile.urls"

USE_TZ = True
LANGUAGE_CODE = "en"
USE_I18N = True

STATIC_URL = "/static/"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django_errors",  # Needed by Wrap Errors
    "axes",  # Needed by SocialProfile [Monitor Logins]
    "user_sessions",  # Needed by SocialProfile [One-Time-Password]
    "django_otp",  # Needed by SocialProfile [One-Time-Password]
    "django_otp.plugins.otp_static",  # Needed by SocialProfile [One-Time-Password]
    "django_otp.plugins.otp_totp",  # Needed by SocialProfile [One-Time-Password]
    "two_factor",  # Needed by SocialProfile [One-Time-Password]
    "social_django",  # Needed by SocialProfile [OAuth]
    "rest_framework.authtoken",  # Needed by SocialProfile [Token]
    "rest_framework",  # Needed by SocialProfile
    "oauth2_provider",  # Needed by SocialProfile [OAuth2 Token]
    "corsheaders",  # Needed by SocialProfile [OAuth2 Token]
    "crispy_forms",  # Needed by SocialProfile [Edit Form]
    "django_countries",  # Needed by SocialProfile [Edit Form]
    "socialprofile",
]

# Social Profile
### Custom Social Profile User

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    # 'django.contrib.sessions.middleware.SessionMiddleware',    # Need Commente-Out By user_sessions
    "user_sessions.middleware.SessionMiddleware",  # Need By SocialProfile
    "django.middleware.cache.UpdateCacheMiddleware",
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",  # Need By SocialProfile
    "django.middleware.locale.LocaleMiddleware",
    "django_otp.middleware.OTPMiddleware",  # Need By SocialProfile
    "corsheaders.middleware.CorsMiddleware",  # Need By SocialProfile
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "axes.middleware.AxesMiddleware",
)

# ------------------------
# Need by Social Profile / user_sessions
SESSION_ENGINE = "user_sessions.backends.db"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

# Core Authentication Settings
LOGIN_URL = "/sp/select/"
LOGIN_ERROR_URL = "/sp/select/"
LOGIN_REDIRECT_URL = "/sp/"
DEFAULT_RETURNTO_PATH = "/sp/"

# Custom user's username settings
SP_SET_USERNAME = True

# Social Auth Redirects Settings
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/sp/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/sp/login-error/"
SOCIAL_AUTH_LOGIN_URL = "/sp/select/"
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = "/sp/new-profile/"
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = "/sp/new-association/"

# Custom Social Profile User
AUTH_USER_MODEL = "socialprofile.socialprofile"
SOCIAL_AUTH_USER_MODEL = "socialprofile.socialprofile"

SOCIAL_AUTH_RAISE_EXCEPTIONS = True

SOCIAL_AUTH_STRATEGY = "social_django.strategy.DjangoStrategy"
SOCIAL_AUTH_STORAGE = "social_django.models.DjangoStorage"

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.mail.mail_validation",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.debug.debug",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "social_core.pipeline.debug.debug",
    "socialprofile.pipeline.socialprofile_extra_values",
)

SOCIAL_AUTH_ALWAYS_ASSOCIATE = True
SOCIAL_AUTH_PROTECTED_USER_FIELDS = [
    "username",
    "email",
    "first_name",
    "last_name",
]
# SOCIAL_AUTH_IMMUTABLE_USER_FIELDS = ["username", "email", "first_name", "last_name", ]
SOCIAL_AUTH_REVOKE_TOKENS_ON_DISCONNECT = True


AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.facebook.FacebookAppOAuth2',
    # 'social_core.backends.facebook.FacebookOAuth2',
    "social_core.backends.google.GoogleOAuth2",
    # 'social_core.backends.instagram.InstagramOAuth2',
    # 'social_core.backends.linkedin.LinkedinOAuth2',
    # 'social_core.backends.live.LiveOAuth2',
    "social_core.backends.twitter.TwitterOAuth",
    # 'social_core.backends.yahoo.YahooOAuth',
    # 'social_core.backends.vimeo.VimeoOAuth1',
    "social_core.backends.email.EmailAuth",
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
)

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
# SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
#     "https://www.googleapis.com/auth/plus.login",
#     "https://www.googleapis.com/auth/user.birthday.read",
#     "https://www.googleapis.com/auth/user.gender.read"
# ]

# AUTHENTICATION_BACKENDS = (
#     # 'django.contrib.auth.backends.ModelBackend',  # Comment if you want DISABLE Login Form (Password)
#     "social.backends.amazon.AmazonOAuth2",
#     "social.backends.angel.AngelOAuth2",
#     "social.backends.aol.AOLOpenId",
#     "social.backends.appsfuel.AppsfuelOAuth2",
#     "social.backends.beats.BeatsOAuth2",
#     "social.backends.behance.BehanceOAuth2",
#     "social.backends.belgiumeid.BelgiumEIDOpenId",
#     "social.backends.bitbucket.BitbucketOAuth",
#     "social.backends.box.BoxOAuth2",
#     "social.backends.clef.ClefOAuth2",
#     "social.backends.coinbase.CoinbaseOAuth2",
#     # 'social.backends.coursera.CourseraOAuth2',
#     "social.backends.dailymotion.DailymotionOAuth2",
#     "social.backends.disqus.DisqusOAuth2",
#     "social.backends.douban.DoubanOAuth2",
#     # 'social.backends.dropbox.DropboxOAuth',
#     "social.backends.dropbox.DropboxOAuth2",
#     # 'social.backends.eveonline.EVEOnlineOAuth2',
#     "social.backends.evernote.EvernoteSandboxOAuth",
#     "social.backends.facebook.FacebookAppOAuth2",
#     "social.backends.facebook.FacebookOAuth2",
#     "social.backends.fedora.FedoraOpenId",
#     "social.backends.fitbit.FitbitOAuth",
#     "social.backends.flickr.FlickrOAuth",
#     "social.backends.foursquare.FoursquareOAuth2",
#     "social.backends.github.GithubOAuth2",
#     # 'social.backends.google.GoogleOAuth',
#     "social.backends.google.GoogleOAuth2",
#     # 'social.backends.google.GoogleOpenId',
#     # 'social.backends.google.GooglePlusAuth',
#     # 'social.backends.google.GoogleOpenIdConnect',
#     "social.backends.instagram.InstagramOAuth2",
#     "social.backends.jawbone.JawboneOAuth2",
#     "social.backends.kakao.KakaoOAuth2",
#     "social.backends.linkedin.LinkedinOAuth",
#     "social.backends.linkedin.LinkedinOAuth2",
#     "social.backends.live.LiveOAuth2",
#     "social.backends.livejournal.LiveJournalOpenId",
#     "social.backends.mailru.MailruOAuth2",
#     "social.backends.mendeley.MendeleyOAuth",
#     "social.backends.mendeley.MendeleyOAuth2",
#     # 'social.backends.mineid.MineIDOAuth2',
#     "social.backends.mixcloud.MixcloudOAuth2",
#     # 'social.backends.nationbuilder.NationBuilderOAuth2',
#     "social.backends.odnoklassniki.OdnoklassnikiOAuth2",
#     "social.backends.open_id.OpenIdAuth",
#     "social.backends.openstreetmap.OpenStreetMapOAuth",
#     "social.backends.persona.PersonaAuth",
#     "social.backends.podio.PodioOAuth2",
#     "social.backends.rdio.RdioOAuth1",
#     "social.backends.rdio.RdioOAuth2",
#     "social.backends.readability.ReadabilityOAuth",
#     "social.backends.reddit.RedditOAuth2",
#     "social.backends.runkeeper.RunKeeperOAuth2",
#     "social.backends.skyrock.SkyrockOAuth",
#     "social.backends.soundcloud.SoundcloudOAuth2",
#     "social.backends.spotify.SpotifyOAuth2",
#     "social.backends.stackoverflow.StackoverflowOAuth2",
#     "social.backends.steam.SteamOpenId",
#     "social.backends.stocktwits.StocktwitsOAuth2",
#     "social.backends.stripe.StripeOAuth2",
#     "social.backends.suse.OpenSUSEOpenId",
#     "social.backends.thisismyjam.ThisIsMyJamOAuth1",
#     "social.backends.trello.TrelloOAuth",
#     "social.backends.tripit.TripItOAuth",
#     "social.backends.tumblr.TumblrOAuth",
#     "social.backends.twilio.TwilioAuth",
#     "social.backends.twitter.TwitterOAuth",
#     "social.backends.vk.VKOAuth2",
#     "social.backends.weibo.WeiboOAuth2",
#     # 'social.backends.wunderlist.WunderlistOAuth2',
#     "social.backends.xing.XingOAuth",
#     "social.backends.yahoo.YahooOAuth",
#     "social.backends.yahoo.YahooOpenId",
#     "social.backends.yammer.YammerOAuth2",
#     "social.backends.yandex.YandexOAuth2",
#     "social.backends.vimeo.VimeoOAuth1",
#     "social.backends.lastfm.LastFmAuth",
#     "social.backends.moves.MovesOAuth2",
#     # 'social.backends.vend.VendOAuth2',
#     "social.backends.email.EmailAuth",
#     "social.backends.username.UsernameAuth",
# )

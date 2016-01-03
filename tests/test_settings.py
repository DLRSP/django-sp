## APP Settings
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Leave Enabled for Admin Access
    'social.backends.google.GoogleOAuth2',
    'social.backends.live.LiveOAuth2',
    'social.backends.yahoo.YahooOpenId',
    'social.backends.weibo.WeiboOAuth2',
    'social.backends.mailru.MailruOAuth2',
    'social.backends.coinbase.CoinbaseOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.tumblr.TumblrOAuth',
    'social.backends.instagram.InstagramOAuth2',
    'social.backends.dropbox.DropboxOAuth2',
    'social.backends.disqus.DisqusOAuth2',
    'social.backends.linkedin.LinkedinOAuth2',
    'social.backends.github.GithubOAuth2',
    'social.backends.flickr.FlickrOAuth',
    'social.backends.yammer.YammerOAuth2',
    # 'social.backends.vimeo.VimeoOAuth1',
)

SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.debug.debug',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'socialprofile.pipeline.socialprofile_extra_values',
    'social.pipeline.debug.debug'
)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/dashboard/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/dashboard/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/dashboard/'
DEFAULT_RETURNTO_PATH = '/sp/'

# Core Authentication Settings
LOGIN_URL = '/sp/select/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGIN_ERROR_URL = '/sp/select/'
##

SECRET_KEY = 'fake-key'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests.db',
        'SUPPORTS_TRANSACTIONS': 'false',
    }
}
ROOT_URLCONF = 'socialprofile.urls'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'socialprofile'
]
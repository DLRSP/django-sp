It's an app to for social authentication and other security integrations.

---

## Requirements

These packages are required:

* Python (3.9+)
* Django (3.2+)

We **highly recommend** and only officially support the latest patch release of each Python and Django series.


## Installation

1. Install using `pip`, including any optional packages you want...

    ``` shell
    pip install django-sp
    ```

    ...or clone the project from github.

    ``` shell
    git clone https://github.com/DLRSP/django-sp/
    ```

2. Add `"socialprofile"` and dependencies apps to your `INSTALLED_APPS` setting.

    ``` python title="settings.py"
    INSTALLED_APPS = [
        ...
        "django_errors",                       # Needed by Wrap Errors
        "axes",                                # Needed by SocialProfile [Monitor Logins]
        "user_sessions",                       # Needed by SocialProfile [One-Time-Password]
        "django_otp",                          # Needed by SocialProfile [One-Time-Password]
        "django_otp.plugins.otp_static",       # Needed by SocialProfile [One-Time-Password]
        "django_otp.plugins.otp_totp",         # Needed by SocialProfile [One-Time-Password]
        "two_factor",                          # Needed by SocialProfile [One-Time-Password]
        "social_django",                       # Needed by SocialProfile [OAuth]
        "rest_framework.authtoken",            # Needed by SocialProfile [Token]
        "rest_framework",                      # Needed by SocialProfile
        "oauth2_provider",                     # Needed by SocialProfile [OAuth2 Token]
        "corsheaders",                         # Needed by SocialProfile [OAuth2 Token]
        "crispy_forms",                        # Needed by SocialProfile [Edit Form]
        "django_countries",                    # Needed by SocialProfile [Edit Form]
        "sweetify",                            # Needed by SocialProfile [Edit Form]
        "socialprofile",
        ...
    ]
    ```

3. Add the following to your root `urls.py` file.

    ``` python title="urls.py"
    # ...other imports...
    from django.conf.urls import url, include

    urlpatterns = [
        url(r'^sp/', include('socialprofile.urls')),
        # ...other urls...
    ]
    ```

4. Add and modify the following middleware inside your `MIDDLEWARE` setting.

    ``` python title="settings.py"
    MIDDLEWARE = (
        "django.middleware.security.SecurityMiddleware",
        # "django.contrib.sessions.middleware.SessionMiddleware",           # Need Commente-Out By user_sessions
        "user_sessions.middleware.SessionMiddleware",                       # Need By SocialProfile
        "django.middleware.cache.UpdateCacheMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "oauth2_provider.middleware.OAuth2TokenMiddleware",                 # Need By SocialProfile
        "django.middleware.locale.LocaleMiddleware",
        "django_otp.middleware.OTPMiddleware",                              # Need By SocialProfile
        "corsheaders.middleware.CorsMiddleware",                            # Need By SocialProfile
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "django.middleware.cache.FetchFromCacheMiddleware",
        "social_django.middleware.SocialAuthExceptionMiddleware",           # Need By SocialProfile
        "axes.middleware.AxesMiddleware",                                   # Need By SocialProfile
    )
    ```

5. Add the following admin error inside your `SILENCED_SYSTEM_CHECKS` setting.

    ``` python title="settings.py"
    SILENCED_SYSTEM_CHECKS = ['admin.E410']  # Need By SocialProfile
    ```

6. Add the following context processor inside your `TEMPLATES` setting.

    ``` python title="settings.py"
    TEMPLATES = [
       {
           ...
           'OPTIONS': {
               'context_processors': [
                   'django.template.context_processors.debug',
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
                   'django.template.context_processors.media',
                   'social_django.context_processors.backends',             # Need By SocialProfile
                   'social_django.context_processors.login_redirect',       # Need By SocialProfile
               ],
           },
       },
    ]
    ```

7. Add the following .... `XxX` setting.

    ``` python title="settings.py"
    # Need by Social Profile / user_sessions
    GEOIP_PATH = '/home/sh/SH_CusData/intf/in/geoip2'
    SESSION_ENGINE = 'user_sessions.backends.db'
    ```

8. Add the following .... `XxX` setting.

    ``` python title="settings.py"
    # Core Authentication Settings
    LOGIN_URL = '/sp/select/'
    LOGIN_ERROR_URL = '/sp/select/'
    LOGIN_REDIRECT_URL = '/sp/'
    DEFAULT_RETURNTO_PATH = '/sp/'

    # Social Auth Redirects Settings
    SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/sp/'
    SOCIAL_AUTH_LOGIN_ERROR_URL = '/sp/login-error/'
    SOCIAL_AUTH_LOGIN_URL = '/sp/select/'
    SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/sp/new-profile/'
    SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/sp/new-association/'
    ```

9. Add the following .... `XxX` setting.

    ``` python title="settings.py"
    # Custom Social Profile User
    AUTH_USER_MODEL = "socialprofile.socialprofile"
    SOCIAL_AUTH_USER_MODEL = 'socialprofile.socialprofile'
    ```

10. Add the following .... `XxX` setting.

    ``` python title="settings.py"
    SOCIAL_AUTH_ALWAYS_ASSOCIATE = True
    SOCIAL_AUTH_PROTECTED_USER_FIELDS = ["username", "email", "first_name", "last_name", ]
    ```

11. Add the following .... `XxX` setting.

    ``` python title="settings.py"
    AUTHENTICATION_BACKENDS = (
       'social_core.backends.google.GoogleOAuth2',
       'social_core.backends.twitter.TwitterOAuth',
       'social_core.backends.email.EmailAuth',
       'axes.backends.AxesBackend',
       'django.contrib.auth.backends.ModelBackend',
    )
    ```

12. Add the following .... `XxX` setting.

    ``` python title="settings.py"
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'aaaaaaaaaaaa-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.apps.googleusercontent.com'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxx'
    SOCIAL_AUTH_TWITTER_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaa'
    SOCIAL_AUTH_TWITTER_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ```


## Example

Let's take a look at a quick example of using this project to build a simple App with **custom social login**.

* Browser the demo app on-line on [Heroku][sandbox]
* Check the demo repo on [GitHub][github-demo]

## Quickstart

Can't wait to get started? The [quickstart guide][quickstart] is the fastest way to get up and running and building a **demo App**.

## Customize

Do you want custom solutions? The [customize][customize] section is an overview of which part are easy to design.
If you find how to personalize different scenarios or behaviors, a [pull request][pull-request] is welcome!

## Development

See the [Contribution guidelines][contributing] for information on how to clone  the repository, run the test suite and contribute changes back to django-errors.

## Security

If you believe you’ve found something in this project which has security implications, please **do not raise the issue in a public forum**.

Send a description of the issue via email to [dlrsp.issue@gmail.com][security-mail].  The project maintainers will then work with you to resolve any issues where required, prior to any public disclosure.

## License

MIT License

Copyright (c) 2010-present DLRSP (https://dlrsp.org) and other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[index]: .
[sandbox]: https://django-sp.herokuapp.com/
[github-demo]: https://github.com/DLRSP/example/tree/django-sp

[quickstart]: tutorial/example.md

[contributing]: community/contributing.md
[pull-request]: community/contributing.png#pull-request

[security-mail]: mailto:dlrsp.issue@gmail.com

# django-sp

[![CI](https://github.com/DLRSP/django-sp/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-sp/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/django-sp.svg)](https://pypi.org/project/django-sp/)
[![Docs](https://img.shields.io/badge/docs-github.io-blue.svg)](https://dlrsp.github.io/django-sp/)

Django social profile authentication: OAuth providers, optional two-factor auth, session hardening, and a customizable user profile.

## Why use it

- Social login via python-social-auth without building provider wiring from scratch
- Extended user profile (avatar, contact fields, preferences)
- Optional TOTP / two-factor authentication
- Login monitoring and session listing helpers
- OAuth2 toolkit and DRF-friendly token surfaces
- Optional dual-write to django-party external identities (`[party]` extra)

## Requirements

- Python 3.10+
- Django 3.2+ (4.2+ recommended)

## Install

```bash
pip install django-sp
```

Optional Party identity sync:

```bash
pip install "django-sp[party]"
```

## Quickstart

```python
INSTALLED_APPS = [
    # ...
    "socialprofile",
]

urlpatterns = [
    path("sp/", include("socialprofile.urls")),
]
```

```bash
python manage.py migrate
```

Configure OAuth backends and site settings as described in the documentation.

## Documentation

- Docs: https://dlrsp.github.io/django-sp/
- PyPI: https://pypi.org/project/django-sp/
- Source: https://github.com/DLRSP/django-sp

## License

MIT

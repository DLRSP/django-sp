# django-sp [![PyPi license](https://img.shields.io/pypi/l/django-sp.svg)](https://pypi.python.org/pypi/django_sp)

## Pypi [![PyPi status](https://img.shields.io/pypi/status/django-sp.svg)](https://pypi.python.org/pypi/django_ps) [![PyPi version](https://img.shields.io/pypi/v/django-sp.svg)](https://pypi.python.org/pypi/django_sp) [![Python version](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13-blue.svg)]() [![PyPi downloads](https://img.shields.io/pypi/dm/django-sp.svg)](https://pypi.python.org/pypi/django_sp) [![PyPi downloads](https://img.shields.io/pypi/dw/django-sp.svg)](https://pypi.python.org/pypi/django_sp) [![PyPi downloads](https://img.shields.io/pypi/dd/django-sp.svg)](https://pypi.python.org/pypi/django_sp)

	$ pip install django-sp

## GitHub ![GitHub release](https://img.shields.io/github/tag/DLRSP/django-sp.svg) ![GitHub release](https://img.shields.io/github/release/DLRSP/django-sp.svg)

## Test [![codecov.io](https://codecov.io/github/DLRSP/django-sp/coverage.svg?branch=main)](https://codecov.io/github/DLRSP/django-sp?branch=main)

Report Issues with [***waffle.io***](https://waffle.io/DLRSP/django-sp/join)

## Run Example Project

	$ git clone https://github.com/DLRSP/example -b django-sp
	$ cd example
	$ python manage.py runserver

Now you browser the app @ http://127.0.0.1:8000


from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username="dlrsp.dev")
user.is_staff = True
user.is_admin = True
user.is_superuser = True
user.save()


# Get current user model from settings
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_user('myemail@crazymail.com', 'mypassword')
user.first_name = 'Tyrone'
user.last_name = 'Citizen'
user.save()

from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_user('myemail@crazymail.com', 'mypassword', 'myemail')
user.first_name = 'Tyrone'
user.last_name = 'Citizen'
user.save()


# Error
ERROR 2023-12-29 13:19:35,275 log 1728326 139722162782720 Internal Server Error: /it/sp/complete/google-oauth2/
Traceback (most recent call last):
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/django/views/decorators/cache.py", line 62, in _wrapper_view_func
    response = view_func(request, *args, **kwargs)
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/django/views/decorators/csrf.py", line 56, in wrapper_view
    return view_func(*args, **kwargs)
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/social_django/utils.py", line 49, in wrapper
    return func(request, backend, *args, **kwargs)
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/social_django/views.py", line 31, in complete
    return do_complete(
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/social_core/actions.py", line 49, in do_complete
    user = backend.complete(user=user, *args, **kwargs)
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/social_core/backends/base.py", line 39, in complete
    return self.auth_complete(*args, **kwargs)
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/social_core/utils.py", line 253, in wrapper
    return func(*args, **kwargs)
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/social_core/backends/oauth.py", line 408, in auth_complete
    state = self.validate_state()
  File "/srv/https/horoscopus/venv/lib64/python3.9/site-packages/social_core/backends/oauth.py", line 98, in validate_state
    raise AuthStateMissing(self, "state")
social_core.exceptions.AuthStateMissing: Session value state missing.
[pid: 1728326|app: 0|req: 2/7] 101.58.43.45 () {58 vars in 2160 bytes} [Fri Dec 29 13:19:34 2023] GET /it/sp/complete/google-oauth2/?state=Kj9FhLkpwVsqBWUkgy3q39RHHNGc4VwQ&code=4%2F0AfJohXn_cVSNiHzqdSvVNFQuNFQfLIqVgevVI_nBnxJr-EgCjQaHURyzbrnbKT6agmlPEg&scope=email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+openid&authuser=0&prompt=none => generated 14583 bytes in 489667 micros (HTTP/2.0 500) 9 headers in 434 bytes (1 switches on core 0)
[pid: 1728327|app: 0|req: 5/8] 101.58.43.45 () {54 vars in 1672 bytes} [Fri Dec 29 13:19:35 2023] GET /it/jsi18n/ => generated 8405 bytes in 2761 micros (HTTP/2.0 200) 10 headers in 335 bytes (1 switches on core 0)

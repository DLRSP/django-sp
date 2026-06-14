# django-sp [![PyPi license](https://img.shields.io/pypi/l/django-sp.svg)](https://pypi.python.org/pypi/django_sp)

## Pypi [![PyPi status](https://img.shields.io/pypi/status/django-sp.svg)](https://pypi.python.org/pypi/django_ps) [![PyPi version](https://img.shields.io/pypi/v/django-sp.svg)](https://pypi.python.org/pypi/django_sp) [![Python version](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13-blue.svg)]() [![PyPi downloads](https://img.shields.io/pypi/dm/django-sp.svg)](https://pypi.python.org/pypi/django_sp) [![PyPi downloads](https://img.shields.io/pypi/dw/django-sp.svg)](https://pypi.python.org/pypi/django_sp) [![PyPi downloads](https://img.shields.io/pypi/dd/django-sp.svg)](https://pypi.python.org/pypi/django_sp)

	$ pip install django-sp

## GitHub ![GitHub release](https://img.shields.io/github/tag/DLRSP/django-sp.svg) ![GitHub release](https://img.shields.io/github/release/DLRSP/django-sp.svg)

## Test [![codecov.io](https://codecov.io/github/DLRSP/django-sp/coverage.svg?branch=main)](https://codecov.io/github/DLRSP/django-sp?branch=main)



## Run Example Project

	$ git clone https://github.com/DLRSP/example -b django-sp
	$ cd example
	$ python manage.py runserver




from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username=\"example-user\")
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
  File "[redacted-path]", line 55, in inner
    response = get_response(request)
  File "[redacted-path]", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "[redacted-path]", line 62, in _wrapper_view_func
    response = view_func(request, *args, **kwargs)
  File "[redacted-path]", line 56, in wrapper_view
    return view_func(*args, **kwargs)
  File "[redacted-path]", line 49, in wrapper
    return func(request, backend, *args, **kwargs)
  File "[redacted-path]", line 31, in complete
    return do_complete(
  File "[redacted-path]", line 49, in do_complete
    user = backend.complete(user=user, *args, **kwargs)
  File "[redacted-path]", line 39, in complete
    return self.auth_complete(*args, **kwargs)
  File "[redacted-path]", line 253, in wrapper
    return func(*args, **kwargs)
  File "[redacted-path]", line 408, in auth_complete
    state = self.validate_state()
  File "[redacted-path]", line 98, in validate_state
    raise AuthStateMissing(self, "state")
social_core.exceptions.AuthStateMissing: Session value state missing.



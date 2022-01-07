from functools import wraps

from django.shortcuts import render
from django.template import RequestContext


# ToDo: not needed !?
def render_to(tpl):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            out = func(request, *args, **kwargs)
            if isinstance(out, dict):
                out = render(tpl, out, RequestContext(request))
            return out

        return wrapper

    return decorator

from axes.helpers import get_client_ip_address, get_client_user_agent
from django.contrib.auth import authenticate
from django.http import HttpRequest, QueryDict
from oauth2_provider.oauth2_validators import OAuth2Validator


class AxesOAuth2Validator(OAuth2Validator):
    def validate_user(self, username, password, client, request, *args, **kwargs):
        """
        Check username and password correspond to a valid and active User
        Set defaults for necessary request object attributes for Axes compatibility.
        The ``request`` argument is not a Django ``HttpRequest`` object.
        """
        _request = request
        if request and not isinstance(request, HttpRequest):
            request = HttpRequest()
            request.uri = _request.uri
            request.method = request.http_method = _request.http_method
            request.META = request.headers = _request.headers
            request._params = _request._params
            request.decoded_body = _request.decoded_body
            request.axes_ip_address = get_client_ip_address(request)
            request.axes_user_agent = get_client_user_agent(request)
            body = QueryDict(str(_request.body), mutable=True)
            if request.method == "GET":
                request.GET = body
            elif request.method == "POST":
                request.POST = body
        user = authenticate(request=request, username=username, password=password)
        if user is not None and user.is_active:
            request = _request
            request.user = user
            return True
        return False

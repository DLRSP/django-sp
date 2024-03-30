"""Test's urls view for django-errors"""

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from django_errors import views as errors_views

urlpatterns = [
    path("", include("django_errors.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    re_path(r"^jsi18n/$", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    re_path(r"^sp/", include("socialprofile.urls")),
)


# @># Server Errors Handlers
handler400 = errors_views.custom_400
""" Handle 400 error """

handler403 = errors_views.custom_403
""" Handle 403 error """

handler404 = errors_views.custom_404
""" Handle 404 error """

handler500 = errors_views.custom_500
""" Handle 500 error """

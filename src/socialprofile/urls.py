"""
Master URL Pattern List for the application.  Most of the patterns here should be top-level
pass-offs to sub-modules, who will have their own urls.py defining actions within.
"""

from django.conf.urls import include
from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from django.views.decorators.cache import never_cache

# from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from . import views

urlpatterns = [
    # Profile Self View
    path(
        "",
        never_cache(login_required(views.SocialProfileView.as_view())),
        name="sp_profile_view",
    ),
    path("login/", never_cache(login_required(views.home))),
    path("logout/", never_cache(views.logout), name="sp_logout_page"),
    path("done/", views.done, name="done"),
    # re_path(r'^ajax-auth/(?P<backend>[^/]+)/$', views.ajax_auth, name='ajax-auth'),
    # New Profile
    path(
        "new-profile/",
        login_required(views.SocialProfileWelcome.as_view()),
        name="new_profile",
    ),
    # New Profile's Association
    path(
        "new-association/",
        login_required(views.SocialProfileView.as_view()),
        name="new_profile_association",
    ),
    # Login Error
    path(
        "login-error/",
        login_required(views.SocialProfileView.as_view()),
        name="login_error",
    ),
    # Login Error
    path(
        "inactive/",
        login_required(views.SocialProfileView.as_view()),
        name="inactive",
    ),
    # Profile Disconnected
    path(
        "profile-disconnected/",
        login_required(views.SocialProfileView.as_view()),
        name="profile_disconnected",
    ),
    # Profile View All
    path(
        "view/all/",
        login_required(views.SocialProfileViewAll.as_view()),
        name="sp_profile_view_all",
    ),
    # Profile Other View
    re_path(
        r"^view/(?P<username>\w.+)/$",
        login_required(views.SocialProfileView.as_view()),
        name="sp_profile_other_view_page",
    ),
    # Profile Edit
    path(
        # "edit/<str:username>/",
        "edit/<int:pk>/",
        never_cache(login_required(views.SocialProfileEditView.as_view())),
        name="sp_profile_edit_page",
    ),
    # Select Sign Up Method
    path("select/", never_cache(views.SelectAuthView.as_view()), name="sp_select_page"),
    # Delete
    path(
        "delete/",
        login_required(views.DeleteSocialProfileView.as_view()),
        name="sp_delete_page",
    ),
    # Social Auth
    path("", include("social_django.urls", namespace="social")),
    # User Sessions
    path("", include("user_sessions.urls", "user_sessions")),
    # OAuth2 Token
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    # Rest Framework
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # path("api-token-auth/", obtain_jwt_token),
    # path("api-token-refresh/', refresh_jwt_token),
    # path("api-token-verify/", verify_jwt_token),
    # One-Time-Password
    # path("", include('two_factor.urls', 'two_factor')),
    # path("check_username_exist/", login_required(views.check_username_exist), name="check_username_exist"),
]

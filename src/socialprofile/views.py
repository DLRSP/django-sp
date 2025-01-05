"""Django Views for the socialprofile module"""

import json
import logging

import sweetify
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView, TemplateView, UpdateView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import permissions, viewsets
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.backends.utils import load_backends
from social_django.utils import psa

from .decorators import render_to
from .forms import SocialProfileForm
from .models import SocialProfile

# from .serializers import SocialProfileSerializer, GroupSerializer
from .serializers import SocialProfileSerializer

LOGGER = logging.getLogger(name="socialprofile.views")

DEFAULT_RETURNTO_PATH = getattr(settings, "DEFAULT_RETURNTO_PATH", "/")


# todo: avoid alert with unique username with table column
# @csrf_exempt
# def check_username_exist(request):
#     username=request.POST.get("username")
#     user = get_user_model()
#     user_obj=user.objects.filter(username=username).exists()
#     if user_obj:
#         return HttpResponse(True)
#     else:
#         return HttpResponse(False)
#


# ViewSets define the view behavior.
class SocialProfileViewSet(viewsets.ModelViewSet):
    """Serialize SocialProfiles"""

    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = SocialProfile.objects.all()
    serializer_class = SocialProfileSerializer


# class GroupViewSet(viewsets.ModelViewSet):
#     """Serialize Groups"""
#     permission_classes = [permissions.IsAuthenticated, TokenHasScope]
#     required_scopes = ['groups']
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect("sp_select_page")


def context(**extra):
    return dict(
        {
            # "plus_id": getattr(settings, "SOCIAL_AUTH_GOOGLE_PLUS_KEY", None),
            # "plus_scope": " ".join(GooglePlusAuth.DEFAULT_SCOPE),
            "available_backends": load_backends(settings.AUTHENTICATION_BACKENDS),
        },
        **extra,
    )


@render_to("socialprofile/sp_account_select.html")
def home(request):
    """Home view, displays login mechanism"""
    if request.user.is_authenticated:
        return redirect("done")
    return context()


@login_required
@render_to("socialprofile/sp_account_select.html")
def done(request):
    """Login complete view, displays user data"""
    if request.user.is_authenticated:
        return context()
    return redirect("sp_select_page")


@psa("social:complete")
def ajax_auth(request, backend):
    if isinstance(request.backend, BaseOAuth1):
        token = {
            "oauth_token": request.REQUEST.get("access_token"),
            "oauth_token_secret": request.REQUEST.get("access_token_secret"),
        }
    elif isinstance(request.backend, BaseOAuth2):
        token = request.REQUEST.get("access_token")
    else:
        raise HttpResponseBadRequest(_("Wrong backend type"))
    user = request.backend.do_auth(token, ajax=True)
    login(request, user)
    data = {"id": user.id, "username": user.username}
    return HttpResponse(json.dumps(data), mimetype="application/json")


class SelectAuthView(TemplateView):
    """
    Lets users choose how they want to request access.

    url: /select
    """

    template_name = "socialprofile/sp_account_select.html"

    def get_context_data(self, **kwargs):
        """Ensure that 'next' gets passed along"""
        LOGGER.debug("socialprofile.views.SelectAuthView.get_context_data")

        next_url = self.request.GET.get(REDIRECT_FIELD_NAME, DEFAULT_RETURNTO_PATH)

        context = super().get_context_data(**kwargs)
        context["next_param"] = REDIRECT_FIELD_NAME
        context["next_url"] = next_url
        # context["plus_id"] = getattr(settings, "SOCIAL_AUTH_GOOGLE_PLUS_KEY", None)
        # context["plus_scope"] = " ".join(GooglePlusAuth.DEFAULT_SCOPE)
        context["available_backends"] = load_backends(settings.AUTHENTICATION_BACKENDS)
        return context


class SocialProfileWelcome(TemplateView):
    """
    New Profile Page

    url: /sp/new-profile
    """

    template_name = "socialprofile/sp_new_profile.html"


# class SocialProfileView(DetailView):
class SocialProfileView(TemplateView):
    """
    Profile View Page

    url: /sp/view
    """

    model = SocialProfile
    template_name = "socialprofile/sp_profile_view.html"
    http_method_names = {"get"}

    def get_context_data(self, **kwargs):
        """Load up the default data to show in the display form."""
        username = self.kwargs.get("username")
        if username:
            try:
                user = get_object_or_404(SocialProfile, username=username)
            except Exception as e:
                try:
                    user = get_object_or_404(SocialProfile, pk=username)
                except Exception as e:
                    user = get_object_or_404(SocialProfile, pk=self.request.user.pk)
        elif self.request.user.is_authenticated:
            user = get_object_or_404(SocialProfile, pk=self.request.user.pk)
        else:
            raise Http404  # Case where user gets to this view anonymously for non-existent user

        if self.request.user != user and user.visible:
            raise Http404  # Case where user set to be private

        return {
            "user": user,
            "available_backends": load_backends(settings.AUTHENTICATION_BACKENDS),
        }


class SocialProfileViewAll(TemplateView):
    """
    Profile View Page

    url: /sp/view/all
    """

    template_name = "socialprofile/sp_profile_view_all.html"
    http_method_names = {"get"}

    def dispatch(self, request, *args, **kwargs):
        if not getattr(
            settings,
            "SP_VIEW_PUBLIC",
            (
                getattr(settings, "SP_VIEW_PUBLIC_ONLY_ADMIN", False)
                and request.user.is_superuser
            ),
        ):
            return redirect("sp_profile_view")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Load up the default data to show in the display form."""
        return {
            "users": SocialProfile.objects.filter(visible=True),
        }


class SocialProfileEditView(UpdateView):
    """
    Profile Editing View

    url: /sp/edit
    """

    model = SocialProfile
    template_name = "socialprofile/sp_profile_edit.html"
    http_method_names = {"get", "post"}

    def get_context_data(self, **kwargs):
        """Load up the default data to show in the display form."""
        # user_form = UserForm(request.POST, instance=request.user)
        # username = self.kwargs.get("username")
        username = self.kwargs.get("pk")
        if username:
            try:
                user = get_object_or_404(SocialProfile, username=username)
            except Exception as e:
                try:
                    user = get_object_or_404(SocialProfile, pk=username)
                except Exception as e:
                    user = self.request.user
        elif self.request.user.is_authenticated:
            user = self.request.user
        else:
            raise Http404  # Case where user gets to this view anonymously for non-existent user

        if user != self.request.user:
            raise PermissionDenied()

        sp_form = SocialProfileForm(instance=user)
        return {
            "user": user,
            "available_backends": load_backends(settings.AUTHENTICATION_BACKENDS),
            "sp_form": sp_form,
        }

    def post(self, request, *args, **kwargs):
        # user_form = UserForm(request.POST, instance=request.user)
        return_to = self.request.POST.get("returnTo", DEFAULT_RETURNTO_PATH)

        custom_alerts = (
            getattr(settings, "SP_ALERT_LIBRARY", "sweetalert") == "sweetalert"
        )

        # username = self.kwargs.get("username")
        username = self.kwargs.get("pk")
        if username:
            try:
                user = get_object_or_404(SocialProfile, username=username)
            except Exception as e:
                try:
                    user = get_object_or_404(SocialProfile, pk=username)
                except Exception as e:
                    user = self.request.user

        if user != self.request.user:
            raise PermissionDenied()

        sp_form = SocialProfileForm(request.POST, instance=user)
        sp_form.initial["returnTo"] = return_to

        if sp_form.is_valid():
            try:
                sp_form.save()

                if custom_alerts:
                    sweetify.toast(
                        self.request,
                        _("Your profile has been updated."),
                        icon="success",
                        timer=3000,
                    )
                else:
                    messages.add_message(
                        self.request,
                        messages.SUCCESS,
                        _("Your profile has been updated."),
                    )
                return self.render_to_response(
                    {
                        "success": True,
                        "user": user,
                        "available_backends": load_backends(
                            settings.AUTHENTICATION_BACKENDS
                        ),
                        "sp_form": sp_form,
                    }
                )
            except Exception as e:
                if custom_alerts:
                    sweetify.toast(
                        self.request,
                        f"{_('ERROR: Your profile has NOT been updated!')} [{e}]",
                        icon="error",
                        timer=3000,
                    )
                else:
                    messages.add_message(
                        self.request,
                        messages.INFO,
                        f"{_('ERROR: Your profile has NOT been updated!')} [{e}]",
                    )

                return self.render_to_response(
                    {
                        "success": False,
                        "user": user,
                        "available_backends": load_backends(
                            settings.AUTHENTICATION_BACKENDS
                        ),
                        "sp_form": sp_form,
                    }
                )
        else:
            if custom_alerts:
                sweetify.toast(
                    self.request,
                    _("Your profile has NOT been updated!"),
                    icon="error",
                    timer=3000,
                )
                # multi = []
                # for x, err_msg in enumerate(sp_form.errors):
                #     multi.append({f"err_mess_{x}": dict(title='Error', icon='warning',
                #     text=err_msg, toast=True, timer=3000, timerProgressBar='true')})
                #     # sweetify.toast(
                #     #     self.request,
                #     #     err_msg,
                #     #     icon="warning",
                #     #     timer=3000,
                #     # )
                # if multi:
                #     sweetify.multiple(request, *multi[0])
            else:
                messages.add_message(
                    self.request, messages.INFO, _("Your profile has NOT been updated!")
                )

            return self.render_to_response(
                {
                    "success": False,
                    "user": user,
                    "available_backends": load_backends(
                        settings.AUTHENTICATION_BACKENDS
                    ),
                    "sp_form": sp_form,
                }
            )


class DeleteSocialProfileView(DeleteView):
    """
    Account Delete Confirm Modal View

    url: /delete
    """

    model = SocialProfile
    success_url = reverse_lazy("sp_logout_page")

    def get_object(self, queryset=None):
        """Get the object that we are going to delete"""
        return self.request.user

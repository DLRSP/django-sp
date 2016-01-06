"""Django Views for the socialprofile module"""

# pylint: disable=R0901,R0904

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login
from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView, FormView, UpdateView, DeleteView, View
from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _


from decorators import render_to
from models import SocialProfile
from forms import SocialProfileForm

from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from social.apps.django_app.utils import psa

import logging

LOGGER = logging.getLogger(name='socialprofile')

DEFAULT_RETURNTO_PATH = getattr(settings, 'DEFAULT_RETURNTO_PATH', '/')

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')

def context(**extra):
    return dict({
        'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
        'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
        'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS)
    }, **extra)

@render_to('socialprofile/sp_account_select.html')
def home(request):
    """Home view, displays login mechanism"""
    if request.user.is_authenticated():
        return redirect('done')
    return context()

@login_required
@render_to('socialprofile/sp_account_select.html')
def done(request):
    """Login complete view, displays user data"""
    if request.user.is_authenticated():
         return context()
    return redirect('sp_select_page')

@psa('social:complete')
def ajax_auth(request, backend):
    if isinstance(request.backend, BaseOAuth1):
        token = {
            'oauth_token': request.REQUEST.get('access_token'),
            'oauth_token_secret': request.REQUEST.get('access_token_secret'),
        }
    elif isinstance(request.backend, BaseOAuth2):
        token = request.REQUEST.get('access_token')
    else:
        raise HttpResponseBadRequest('Wrong backend type')
    user = request.backend.do_auth(token, ajax=True)
    login(request, user)
    data = {'id': user.id, 'username': user.username}
    return HttpResponse(json.dumps(data), mimetype='application/json')	

class SelectAuthView(TemplateView):
    """
    Lets users choose how they want to request access.

    url: /select
    """
    template_name = 'socialprofile/sp_account_select.html'

    def get_context_data(self, **kwargs):
        """Ensure that 'next' gets passed along"""
        LOGGER.debug('socialprofile.views.SelectAuthView.get_context_data')

        next_url = self.request.GET.get(REDIRECT_FIELD_NAME, DEFAULT_RETURNTO_PATH)

        context = super(SelectAuthView, self).get_context_data(**kwargs)
        context['next_param'] = REDIRECT_FIELD_NAME
        context['next_url'] = next_url
        context['plus_id'] = getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None)
        context['plus_scope'] = ' '.join(GooglePlusAuth.DEFAULT_SCOPE)
        context['available_backends'] = load_backends(settings.AUTHENTICATION_BACKENDS)
        return context


class SocialProfileView(TemplateView):
    """
    Profile View Page

    url: /profile/view
    """
    template_name = 'socialprofile/sp_profile_view.html'

    http_method_names = {'get'}

    def get_context_data(self, **kwargs):
        """Load up the default data to show in the display form."""
        LOGGER.debug("socialprofile.views.SocialProfileView.get_context_data")
        username = self.kwargs.get('username')
        if username:
          try:
             ser = get_object_or_404(SocialProfile, username=username)
          except Exception as e: 
             try:
                user = get_object_or_404(SocialProfile, pk=username)
             except Exception as e: 
                user = self.request.user
        elif self.request.user.is_authenticated():
            user = self.request.user
        else:
            raise Http404  # Case where user gets to this view anonymously for non-existent user

        return_to = self.request.GET.get('returnTo', DEFAULT_RETURNTO_PATH)

        sp_form = SocialProfileForm(instance=user)
        # user_form = UserForm(instance=user)

        sp_form.initial['returnTo'] = return_to

        return {'sp_form': sp_form}


class SocialProfileEditView(SocialProfileView):
    """
    Profile Editing View

    url: /profile/edit
    """

    template_name = 'socialprofile/sp_profile_edit.html'

    http_method_names = {'get', 'post'}

    def post(self, request, *args, **kwargs):
        # user_form = UserForm(request.POST, instance=request.user)
        sp_form = SocialProfileForm(request.POST, instance=request.user)

        # if user_form.is_valid() & sp_form.is_valid():
        if sp_form.is_valid():
            try:
               # user_form.save()
               sp_form.save()
               messages.add_message(self.request, messages.INFO, _('Your profile has been updated.'))
               return HttpResponseRedirect(sp_form.cleaned_data.get('returnTo', DEFAULT_RETURNTO_PATH))
            except Exception as e:
               messages.add_message(self.request, messages.INFO, _('ERROR: Your profile has NOT been updated! ['+str(e)+']'))
               eturn self.render_to_response({'sp_form': sp_form})
        else:
            messages.add_message(self.request, messages.INFO, _('Your profile has NOT been updated.'))
            return self.render_to_response({'sp_form': sp_form})


class DeleteSocialProfileView(DeleteView):
    """
    Account Delete Confirm Modal View

    url: /delete
    """

    success_url = reverse_lazy('sp_logout_page')

    template_name = "socialprofile/sp_delete_account_modal.html"

    model = SocialProfile

    def get_object(self, queryset=None):
        """Get the object that we are going to delete"""
        return self.request.user

"""Django forms for the socialprofile application"""

import logging

from crispy_forms.bootstrap import (
    Accordion,
    AccordionGroup,
    Field,
    InlineRadios,
    PrependedText,
    UneditableField,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.conf import settings
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import CountrySelectWidget

from .models import SocialProfile

LOGGER = logging.getLogger(name="socialprofile.forms")


class CustomImageField(Field):
    template = "socialprofile/image_thumbnail.html"


class SocialProfileForm(forms.ModelForm):
    """Master form for editing the user's profile"""

    # user = forms.IntegerField(widget=forms.HiddenInput, required=True)
    returnTo = forms.CharField(
        widget=forms.HiddenInput, required=False, initial="/"
    )  # URI to Return to after save
    edited_by_user = forms.BooleanField(
        widget=forms.HiddenInput, required=False, initial=True
    )

    date_of_birth = forms.DateField(
        label=_("Date of Birth"),
        widget=forms.TextInput(attrs={"type": "date"}),
        required=False,
    )

    class Meta:
        """Configuration for the ModelForm"""

        model = SocialProfile
        # exclude = [
        #     "is_staff",
        #     "is_superuser",
        #     "is_active",
        #     "password",
        #     "edited_by_provider",
        # ]
        fields = [
            "username",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "email",
            "phone_number",
            "url",
            "image_avatar",
            "image",
            "cropping",
            "image_avatar_predef",
            "google_username",
            "twitter_username",
            "instagram_username",
            "facebook_username",
            "google_email",
            "twitter_email",
            "instagram_email",
            "facebook_email",
            "live_email",
            "country",
            "city",
            "postalcode",
            "address",
            "description",
            "visible",
        ]
        # todo: Avoid bound_field = form[field] missing fields
        # if "google" in str(settings.AUTHENTICATION_BACKENDS):
        #     fields.append("google_email")
        # if "twitter" in str(settings.AUTHENTICATION_BACKENDS):
        #     fields.append("twitter_email")
        # if "instagram" in str(settings.AUTHENTICATION_BACKENDS):
        #     fields.append("instagram_email")
        # if "facebook" in str(settings.AUTHENTICATION_BACKENDS):
        #     fields.append("facebook_email")
        # if "live" in str(settings.AUTHENTICATION_BACKENDS):
        #     fields.append("live_email")

        widgets = {
            "country": CountrySelectWidget(layout="{widget}"),
            "gender": forms.RadioSelect,
            "visible": forms.RadioSelect,
            # "image": ImageCropWidget,
        }

    # Don't let through for security reasons, user should be based on logged in user only
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "sp-edit-form"
        self.helper.render_hidden_fields = True
        self.helper.include_media = False
        # self.helper.form_show_errors = True
        # self.helper.use_custom_control = True

        # disable all mail's fields to avoid hijacking inside html
        for nam, field in self.fields.items():
            if "email" in nam:
                field.disabled = True

        # self.helper.form_show_labels = False
        self.fields["username"].label = False
        # self.fields["country"].label = False
        self.fields["twitter_username"].label = False
        self.fields["facebook_username"].label = False
        self.fields["instagram_username"].label = False

        self.fields["image_avatar"].label = False
        self.fields["image"].label = False
        self.fields["image_avatar_predef"].label = False

        self.helper.label_class = "labels"
        self.helper.field_class = "col-md-12"
        # self.helper.form_class = 'form-vertical'
        # # self.helper.label_class = "col-md-2"
        # # self.helper.field_class = "col-md-10"

        self.helper.layout = Layout(
            Row(
                Field("username"),
                css_class="row mt-2",
            ),
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
                css_class="row mt-2",
            ),
            Row(
                InlineRadios("gender", css_class="col-md-6"),
                Field("date_of_birth"),
                css_class="row mt-3",
            ),
            Accordion(
                AccordionGroup(
                    _("Contact"),
                    # UneditableField("email"),
                    Field("phone_number"),
                    Field("url"),
                    active=False,
                ),
                # AccordionGroup(
                #     _("Avatar"),
                #     InlineRadios("image_avatar", css_class="col-md-6"),
                #     TabHolder(
                #         Tab(
                #             _("Custom"),
                #             # CustomImageField('image'),
                #             Field('image'),
                #             Field("cropping"),
                #             css_class="row mt-3",
                #         ),
                #         Tab(
                #             _("Pre-Defined"),
                #             Field("image_avatar_predef"),
                #             css_class="row mt-3",
                #         ),
                #     ),
                #
                # ),
                AccordionGroup(
                    _("Socials"),
                    Row(
                        PrependedText(
                            "twitter_username",
                            "@",
                            placeholder=f"Twitter {_('Username')}",
                        ),
                        PrependedText(
                            "instagram_username",
                            "@",
                            placeholder=f"Instagram {_('Username')}",
                        ),
                        PrependedText(
                            "facebook_username",
                            "@",
                            placeholder=f"Facebook {_('Username')}",
                        ),
                        css_class="row mt-3",
                    ),
                ),
                AccordionGroup(
                    _("Mails"),
                    Row(
                        Field("email", placeholder=f"Mail", readonly=True),
                        Field(
                            "google_email", placeholder=f"Google Mail", readonly=True
                        ),
                        Field(
                            "twitter_email", placeholder=f"Twitter Mail", readonly=True
                        ),
                        Field(
                            "instagram_email",
                            placeholder=f"Instagram Mail",
                            readonly=True,
                        ),
                        Field(
                            "facebook_email",
                            placeholder=f"Facebook Mail",
                            readonly=True,
                        ),
                        css_class="row mt-3",
                    ),
                ),
                AccordionGroup(
                    _("Address"),
                    PrependedText(
                        "country",
                        mark_safe(
                            f'<img class="country-select-flag" id="flag_id_country" '
                            f'src="{settings.STATIC_URL}flags/it.gif" '
                            f'style="margin: 4px 4px 0" width="25" height="20">'
                        ),
                    ),
                    Row(
                        Column("city", css_class="col-md-6"),
                        Column("postalcode", css_class="col-md-6"),
                        css_class="row mt-2",
                    ),
                    Field("address"),
                ),
                AccordionGroup(
                    _("Info"),
                    Row(
                        Field("description"),
                        css_class="row mt-3",
                    ),
                ),
                AccordionGroup(
                    _("Security"),
                    InlineRadios("visible"),
                ),
            ),
            # ButtonHolder(
            Row(
                Submit(
                    "submit",
                    _("Save"),
                    css_class="text-center profile-button",
                ),
                css_class="row mt-5",
            ),
        )
        # self.helper.fields['email'].initial = "test"

        # for nam, field in self.fields.items():
        #     field.disabled = True

    def clean_description(self):
        """Automatically called by Django, this method 'cleans' the description, e.g. stripping HTML out of desc"""

        LOGGER.debug("socialprofile.forms.SocialProfileForm.clean_description")

        return strip_tags(self.cleaned_data["description"])

    def clean(self):
        """Automatically called by Django, this method 'cleans' the whole form"""

        LOGGER.debug("socialprofile.forms.SocialProfileForm.clean")

        if self.changed_data:
            self.cleaned_data["edited_by_user"] = True

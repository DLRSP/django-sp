from django.conf import settings
from django.template import Context, Template
from django.test import TestCase
from django.utils import translation
from social_core.backends.utils import load_backends


class TestSocialProfileTags(TestCase):

    TEMPLATE_BACKEND_NAME = Template(
        "{% load socialprofile_tags %}{% for sublist in available_backends|social_backends %}{% for name, backend in sublist %}"
        "{{ name }} "
        "{% endfor %}{% endfor %}"
    )
    TEMPLATE_BACKEND_ICON_NAME = Template(
        "{% load socialprofile_tags %}{% for sublist in available_backends|social_backends %}{% for name, backend in sublist %}"
        "{{ name|icon_name }} "
        "{% endfor %}{% endfor %}"
    )
    TEMPLATE_BACKEND_CLASS = Template(
        "{% load socialprofile_tags %}"
        "{% for sublist in available_backends|social_backends %}"
        "{{ sublist }}"
        "{% for name, backend in sublist %}"
        "{{ name }} {{ backend }}"
        "{% endfor %}"
        "{% endfor %}"
    )
    # TEMPLATE_ASSOCIATED = Template(
    #     "{% load socialprofile_tags %}{% available_backends code as country %}{{ country }}"
    # )
    # TEMPLATE_COUNTRY = Template(
    #     "{% load socialprofile_tags %}{% available_backends code as country %}{{ country }}"
    #     "{% load socialprofile_tags %}{% social_backends code as country %}{{ country }}"
    # )
    # TEMPLATE_NAME = Template(
    #     "{% load socialprofile_tags %}{% get_country code as country %}{{ country.name }}"
    # )

    def test_backend_name(self):
        rendered = self.TEMPLATE_BACKEND_NAME.render(
            Context(
                {"available_backends": load_backends(settings.AUTHENTICATION_BACKENDS)}
            )
        )
        self.assertEqual(rendered, "google-oauth2 twitter ")

    def test_backend_icon_name(self):
        rendered = self.TEMPLATE_BACKEND_ICON_NAME.render(
            Context(
                {"available_backends": load_backends(settings.AUTHENTICATION_BACKENDS)}
            )
        )
        self.assertEqual(rendered, "google twitter ")

    # def test_country_name(self):
    #     with translation.override("pt-BR"):
    #         rendered = self.TEMPLATE_NAME.render(Context({"code": "BR"}))
    #     self.assertEqual(rendered, "Brasil")
    #
    # def test_wrong_code(self):
    #     rendered = self.TEMPLATE_COUNTRY.render(Context({"code": "XX"}))
    #     self.assertEqual(rendered, "XX")
    #
    #     rendered = self.TEMPLATE_NAME.render(Context({"code": "XX"}))
    #     self.assertEqual(rendered, "")

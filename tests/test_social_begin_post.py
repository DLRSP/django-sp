"""Regression: social-auth-app-django 6.0+ requires POST to social:begin."""

from __future__ import annotations

from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse

from socialprofile.models import SocialProfile


class LogoutAndSelectAuthTests(TestCase):
    def setUp(self):
        self.user = SocialProfile.objects.create_user(
            "u@example.com", "pwd", "logout_user"
        )

    def test_logout_clears_session_and_lands_on_select(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("sp_logout_page"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("sp_select_page"))
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_select_auth_page_renders_for_anonymous(self):
        response = self.client.get(reverse("sp_select_page"))
        self.assertEqual(response.status_code, 200)

    def test_select_auth_rejects_protocol_relative_next_in_oauth_href(self):
        response = self.client.get(
            reverse("sp_select_page"), {"next": "//evil.example/phish"}
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        if "next=" in body or 'name="next"' in body:
            self.assertNotIn("next=//evil.example", body)
            self.assertNotIn('value="//evil.example', body)

    def test_select_auth_uses_post_forms_for_social_begin(self):
        response = self.client.get(reverse("sp_select_page"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('method="post"', body)
        self.assertIn("/login/", body)
        self.assertNotRegex(body, r'href="[^"]*/login/')

    def test_select_auth_preserves_next_in_post_form(self):
        response = self.client.get(
            reverse("sp_select_page"), {"next": "/sp/profile/"}
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('name="next"', body)
        self.assertIn('value="/sp/profile/"', body)

    def test_social_begin_accepts_post_with_csrf(self):
        select = self.client.get(reverse("sp_select_page"))
        csrf = select.context["csrf_token"]
        response = self.client.post(
            reverse("social:begin", kwargs={"backend": "google-oauth2"}),
            {"csrfmiddlewaretoken": csrf},
        )
        self.assertNotEqual(response.status_code, 405)

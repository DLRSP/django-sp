"""Email password / OTP / trusted-device auth."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from socialprofile.conf import apply_sp_defaults
from socialprofile.email_auth import (
    OTP_MAX_ATTEMPTS,
    SEND_RATE_MAX,
    TRUST_COOKIE,
    create_challenge,
    issue_trusted_device,
    set_password_and_revoke_trust,
    verify_challenge,
)
from socialprofile.models import EmailLoginChallenge, TrustedDevice

User = get_user_model()

EMAIL_FLAGS = {
    "SP_EMAIL_PASSWORD_LOGIN": True,
    "SP_EMAIL_OTP_LOGIN": True,
    "SP_TRUSTED_DEVICE": True,
}

JSON_HEADERS = {"HTTP_ACCEPT": "application/json"}


@override_settings(**EMAIL_FLAGS)
class EmailLoginFlagOffTests(TestCase):
    def test_flag_defaults_off(self):
        settings = {}
        apply_sp_defaults(settings)
        assert settings["SP_EMAIL_PASSWORD_LOGIN"] is False
        assert settings["SP_EMAIL_OTP_LOGIN"] is False
        assert settings["SP_TRUSTED_DEVICE"] is False

    @override_settings(
        SP_EMAIL_PASSWORD_LOGIN=False,
        SP_EMAIL_OTP_LOGIN=False,
        SP_TRUSTED_DEVICE=False,
    )
    def test_endpoints_404_when_flags_off(self):
        c = Client()
        for name in (
            "sp_email_register",
            "sp_email_login",
            "sp_email_otp_request",
            "sp_email_otp_verify",
            "sp_email_password_reset",
            "sp_email_password_reset_confirm",
        ):
            r = c.post(reverse(name), {})
            self.assertEqual(r.status_code, 404, name)
        r = c.get(reverse("sp_email_auth_status"))
        self.assertEqual(r.status_code, 404)


class EmailAuthOverlayTests(TestCase):
    def test_overlay_removes_associate_and_emailauth(self):
        settings = {
            "SP_EMAIL_PASSWORD_LOGIN": True,
            "SOCIAL_AUTH_PIPELINE": (
                "social_core.pipeline.social_auth.associate_by_email",
                "social_core.pipeline.user.create_user",
            ),
            "AUTHENTICATION_BACKENDS": (
                "social_core.backends.email.EmailAuth",
                "django.contrib.auth.backends.ModelBackend",
            ),
        }
        apply_sp_defaults(settings)
        assert (
            "social_core.pipeline.social_auth.associate_by_email"
            not in settings["SOCIAL_AUTH_PIPELINE"]
        )
        assert (
            "social_core.backends.email.EmailAuth"
            not in settings["AUTHENTICATION_BACKENDS"]
        )
        assert ["username", "ip_address"] in settings["AXES_LOCKOUT_PARAMETERS"]


@override_settings(
    **EMAIL_FLAGS, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class EmailLoginFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        mail.outbox.clear()

    def _otp_from_mail(self):
        self.assertTrue(mail.outbox)
        body = mail.outbox[-1].body
        for token in body.split():
            if token.isdigit() and len(token) == 6:
                return token
        self.fail(f"no otp in mail: {body!r}")

    def _json_post(self, name, data):
        return self.client.post(reverse(name), data, **JSON_HEADERS)

    def test_register_login_welcome(self):
        r = self._json_post(
            "sp_email_register",
            {
                "email": "guest@example.com",
                "password": "ComplexPass!234",
                "password_confirm": "ComplexPass!234",
            },
        )
        self.assertEqual(r.status_code, 200)
        reg = r.json()
        self.assertTrue(reg.get("ok"))
        self.assertEqual(
            reg.get("purpose"), EmailLoginChallenge.PURPOSE_REGISTER
        )
        self.assertEqual(reg.get("next_step"), "otp")
        user = User.objects.get(email="guest@example.com")
        self.assertTrue(user.check_password("ComplexPass!234"))
        self.assertIsNone(user.email_verified_at)
        code = self._otp_from_mail()
        r = self._json_post(
            "sp_email_otp_verify",
            {
                "email": "guest@example.com",
                "code": code,
                "purpose": reg.get("purpose"),
            },
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data.get("ok"))
        self.assertIn("/sp/new-profile/", data.get("redirect", ""))
        user.refresh_from_db()
        self.assertIsNotNone(user.email_verified_at)
        for ch in EmailLoginChallenge.objects.filter(email="guest@example.com"):
            self.assertNotEqual(ch.code_hash, code)
            self.assertNotIn(code, ch.code_hash)

    def test_browser_form_redirects_without_json(self):
        r = self.client.post(
            reverse("sp_email_otp_request"),
            {"email": "nobody@example.com"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], reverse("sp_select_page"))
        self.assertNotIn("application/json", r.get("Content-Type", ""))

    def test_ajax_otp_request_returns_json_toast_payload(self):
        r = self._json_post(
            "sp_email_otp_request", {"email": "nobody@example.com"}
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("next_step"), "otp")
        self.assertIn("sent instructions", data.get("detail", "").lower())
        self.assertNotIn("field", data)

    def test_ajax_invalid_otp_is_field_error(self):
        r = self._json_post(
            "sp_email_otp_verify",
            {
                "email": "x@example.com",
                "code": "000000",
                "purpose": EmailLoginChallenge.PURPOSE_LOGIN,
            },
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertFalse(data.get("ok"))
        self.assertEqual(data.get("field"), "code")
        self.assertIn("Invalid or expired", data.get("detail", ""))

    def test_ajax_wrong_password_is_field_error(self):
        u = User(
            email="wp2@example.com",
            username="wp2u",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        r = self._json_post(
            "sp_email_login",
            {"email": "wp2@example.com", "password": "wrong-password-xx"},
        )
        data = r.json()
        self.assertFalse(data.get("ok"))
        self.assertEqual(data.get("field"), "password")

    def test_duplicate_register_no_enum(self):
        User.objects.create(
            email="dup@example.com",
            username="dup1",
            email_verified_at=timezone.now(),
        )
        r1 = self._json_post(
            "sp_email_register",
            {
                "email": "dup@example.com",
                "password": "ComplexPass!234",
                "password_confirm": "ComplexPass!234",
            },
        )
        r2 = self._json_post(
            "sp_email_register",
            {
                "email": "newunique@example.com",
                "password": "ComplexPass!234",
                "password_confirm": "ComplexPass!234",
            },
        )
        self.assertEqual(r1.status_code, r2.status_code)
        self.assertEqual(r1.json().get("ok"), r2.json().get("ok"))
        self.assertNotIn("already", (r1.json().get("detail") or "").lower())

    def test_unverified_reregister_adopts_new_password(self):
        u = User(email="uv@example.com", username="uvu", email_verified_at=None)
        u.set_password("OldComplexPass!111")
        u.save()
        r = self._json_post(
            "sp_email_register",
            {
                "email": "uv@example.com",
                "password": "NewComplexPass!222",
                "password_confirm": "NewComplexPass!222",
            },
        )
        self.assertTrue(r.json().get("ok"))
        u.refresh_from_db()
        self.assertTrue(u.check_password("NewComplexPass!222"))
        self.assertFalse(u.check_password("OldComplexPass!111"))
        self.assertIsNone(u.email_verified_at)

    def test_verified_reregister_keeps_password(self):
        u = User(
            email="vd@example.com",
            username="vdu",
            email_verified_at=timezone.now(),
        )
        u.set_password("KeepComplexPass!333")
        u.save()
        r = self._json_post(
            "sp_email_register",
            {
                "email": "vd@example.com",
                "password": "AttackerPass!444",
                "password_confirm": "AttackerPass!444",
            },
        )
        self.assertTrue(r.json().get("ok"))
        u.refresh_from_db()
        self.assertTrue(u.check_password("KeepComplexPass!333"))
        self.assertFalse(u.check_password("AttackerPass!444"))

    def test_register_password_mismatch(self):
        r = self._json_post(
            "sp_email_register",
            {
                "email": "mm@example.com",
                "password": "ComplexPass!234",
                "password_confirm": "ComplexPass!999",
            },
        )
        data = r.json()
        self.assertFalse(data.get("ok"))
        self.assertEqual(data.get("field"), "password_confirm")

    def test_register_honeypot_silent_success(self):
        before = User.objects.count()
        r = self._json_post(
            "sp_email_register",
            {
                "email": "bot@example.com",
                "password": "ComplexPass!234",
                "password_confirm": "ComplexPass!234",
                "company": "Acme Spam Ltd",
            },
        )
        self.assertTrue(r.json().get("ok"))
        self.assertEqual(User.objects.count(), before)

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {"min_length": 10},
            }
        ]
    )
    def test_register_weak_password_field_error(self):
        r = self._json_post(
            "sp_email_register",
            {
                "email": "weak@example.com",
                "password": "short",
                "password_confirm": "short",
            },
        )
        data = r.json()
        self.assertFalse(data.get("ok"))
        self.assertEqual(data.get("field"), "password")
        self.assertTrue(data.get("detail"))

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {"min_length": 8},
            },
            {
                "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
            },
        ]
    )
    def test_password_too_short_message_is_translated_it(self):
        """Django 5.2 uses %d msgids; package locale must cover them (IT mix bug)."""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        from django.utils import translation

        with translation.override("it"):
            with self.assertRaises(ValidationError) as ctx:
                validate_password("123")
            joined = " ".join(ctx.exception.messages)
        self.assertNotIn("This password is too short", joined)
        self.assertIn("troppo corta", joined.lower())

    def test_password_login_requires_verified(self):
        u = User(email="v@example.com", username="vu")
        u.set_password("ComplexPass!234")
        u.save()
        r = self._json_post(
            "sp_email_login",
            {"email": "v@example.com", "password": "ComplexPass!234"},
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertFalse(data.get("ok"))
        self.assertEqual(data.get("next_step"), "otp")

    def test_password_login_with_otp_stepup(self):
        u = User(
            email="ok@example.com",
            username="oku",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        r = self._json_post(
            "sp_email_login",
            {"email": "ok@example.com", "password": "ComplexPass!234"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("next_step"), "otp")
        code = self._otp_from_mail()
        r = self._json_post(
            "sp_email_otp_verify",
            {
                "email": "ok@example.com",
                "code": code,
                "purpose": EmailLoginChallenge.PURPOSE_LOGIN,
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json().get("ok"))
        self.assertTrue(r.json().get("redirect"))
        r = self.client.get(reverse("sp_select_page"))
        self.assertTrue(r.wsgi_request.user.is_authenticated)

    def test_wrong_password(self):
        u = User(
            email="wp@example.com",
            username="wpu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        r = self._json_post(
            "sp_email_login",
            {"email": "wp@example.com", "password": "wrong-password-xx"},
        )
        self.assertFalse(r.json().get("ok"))

    def test_otp_only_path_ignores_trusted_device_skip(self):
        u = User(
            email="otp@example.com",
            username="otpu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        response = self.client.get(reverse("sp_select_page"))
        issue_trusted_device(u, response.wsgi_request, response)
        cookie_val = response.cookies.get(TRUST_COOKIE)
        if cookie_val:
            self.client.cookies[TRUST_COOKIE] = cookie_val.value
        r = self._json_post(
            "sp_email_otp_request", {"email": "otp@example.com"}
        )
        self.assertTrue(r.json().get("ok"))
        self.assertTrue(mail.outbox)
        code = self._otp_from_mail()
        r = self._json_post(
            "sp_email_otp_verify",
            {
                "email": "otp@example.com",
                "code": code,
                "purpose": EmailLoginChallenge.PURPOSE_LOGIN,
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json().get("ok"))
        self.assertTrue(r.json().get("redirect"))

    def test_trusted_device_cookie_alone_no_session(self):
        u = User(
            email="td@example.com",
            username="tdu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        response = self.client.get(reverse("sp_select_page"))
        issue_trusted_device(u, response.wsgi_request, response)
        cookie_val = response.cookies.get(TRUST_COOKIE)
        c2 = Client()
        if cookie_val:
            c2.cookies[TRUST_COOKIE] = cookie_val.value
        r = c2.get(reverse("sp_select_page"))
        self.assertFalse(r.wsgi_request.user.is_authenticated)

    def test_password_plus_trust_skips_otp(self):
        u = User(
            email="pt@example.com",
            username="ptu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        response = self.client.get(reverse("sp_select_page"))
        issue_trusted_device(u, response.wsgi_request, response)
        cookie_val = response.cookies.get(TRUST_COOKIE)
        self.assertIsNotNone(cookie_val)
        self.client.cookies[TRUST_COOKIE] = cookie_val.value
        mail.outbox.clear()
        r = self.client.post(
            reverse("sp_email_login"),
            {"email": "pt@example.com", "password": "ComplexPass!234"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertFalse(mail.outbox)

    def test_otp_not_totp_device(self):
        create_challenge("x@example.com", EmailLoginChallenge.PURPOSE_LOGIN)
        self.assertEqual(TOTPDevice.objects.count(), 0)
        self.assertEqual(StaticDevice.objects.count(), 0)
        self.assertEqual(EmailLoginChallenge.objects.count(), 1)

    def test_reset_flow(self):
        u = User(
            email="rs@example.com",
            username="rsu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        issue_trusted_device(
            u,
            self.client.get(reverse("sp_select_page")).wsgi_request,
            self.client.get(reverse("sp_select_page")),
        )
        TrustedDevice.objects.filter(user=u).update(
            expires_at=timezone.now() + timedelta(days=1)
        )
        self.assertTrue(
            TrustedDevice.objects.filter(
                user=u, revoked_at__isnull=True
            ).exists()
        )
        r = self._json_post(
            "sp_email_password_reset", {"email": "rs@example.com"}
        )
        self.assertTrue(r.json().get("ok"))
        code = self._otp_from_mail()
        r = self._json_post(
            "sp_email_password_reset_confirm",
            {
                "email": "rs@example.com",
                "code": code,
                "password": "NewComplexPass!567",
            },
        )
        self.assertTrue(r.json().get("ok"))
        u.refresh_from_db()
        self.assertTrue(u.check_password("NewComplexPass!567"))
        self.assertFalse(
            TrustedDevice.objects.filter(
                user=u, revoked_at__isnull=True
            ).exists()
        )

    def test_reset_unknown_email_same_status(self):
        r1 = self._json_post(
            "sp_email_password_reset", {"email": "nouser@example.com"}
        )
        u = User(
            email="known@example.com",
            username="knownu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        r2 = self._json_post(
            "sp_email_password_reset", {"email": "known@example.com"}
        )
        self.assertEqual(r1.status_code, r2.status_code)
        self.assertEqual(r1.json().get("ok"), r2.json().get("ok"))

    def test_otp_request_unknown_no_enum(self):
        r1 = self._json_post(
            "sp_email_otp_request", {"email": "ghost@example.com"}
        )
        u = User(
            email="real@example.com",
            username="realu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        r2 = self._json_post(
            "sp_email_otp_request", {"email": "real@example.com"}
        )
        self.assertEqual(r1.status_code, r2.status_code)
        self.assertEqual(r1.json().get("ok"), r2.json().get("ok"))

    def test_expired_otp_rejected(self):
        u = User(
            email="ex@example.com",
            username="exu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        ch, code = create_challenge(
            "ex@example.com", EmailLoginChallenge.PURPOSE_LOGIN
        )
        ch.expires_at = timezone.now() - timedelta(minutes=1)
        ch.save(update_fields=["expires_at"])
        r = self._json_post(
            "sp_email_otp_verify",
            {
                "email": "ex@example.com",
                "code": code,
                "purpose": EmailLoginChallenge.PURPOSE_LOGIN,
            },
        )
        self.assertFalse(r.json().get("ok"))

    def test_select_hides_disclaimer_when_password_on(self):
        r = self.client.get(reverse("sp_select_page"))
        self.assertNotContains(
            r, "We will never know and store your password anywhere!"
        )

    def test_select_includes_email_wizard_assets(self):
        r = self.client.get(reverse("sp_select_page"))
        self.assertContains(r, "data-sp-email-wizard")
        self.assertContains(r, "email-login.js")

    def test_send_rate_max_blocks_further_challenges(self):
        email = "rate@example.com"
        for _ in range(SEND_RATE_MAX):
            ch, code = create_challenge(
                email, EmailLoginChallenge.PURPOSE_LOGIN, ip="127.0.0.1"
            )
            self.assertIsNotNone(ch)
            self.assertIsNotNone(code)
        ch, code = create_challenge(
            email, EmailLoginChallenge.PURPOSE_LOGIN, ip="127.0.0.1"
        )
        self.assertIsNone(ch)
        self.assertIsNone(code)
        before_mail = len(mail.outbox)
        r = self._json_post("sp_email_otp_request", {"email": email})
        self.assertTrue(r.json().get("ok"))
        self.assertEqual(len(mail.outbox), before_mail)

    def test_otp_max_attempts_rejects_even_correct_code(self):
        email = "attempts@example.com"
        u = User(
            email=email,
            username="attemptsu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        ch, code = create_challenge(email, EmailLoginChallenge.PURPOSE_LOGIN)
        for _ in range(OTP_MAX_ATTEMPTS):
            self.assertIsNone(
                verify_challenge(
                    email, "000000", EmailLoginChallenge.PURPOSE_LOGIN
                )
            )
        self.assertIsNone(
            verify_challenge(email, code, EmailLoginChallenge.PURPOSE_LOGIN)
        )
        r = self._json_post(
            "sp_email_otp_verify",
            {
                "email": email,
                "code": code,
                "purpose": EmailLoginChallenge.PURPOSE_LOGIN,
            },
        )
        self.assertFalse(r.json().get("ok"))

    def test_wrong_password_records_access_attempt(self):
        from axes.models import AccessAttempt

        u = User(
            email="axespwd@example.com",
            username="axespwdu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        before = AccessAttempt.objects.count()
        r = self._json_post(
            "sp_email_login",
            {"email": "axespwd@example.com", "password": "wrong-password-xx"},
        )
        self.assertFalse(r.json().get("ok"))
        self.assertGreater(AccessAttempt.objects.count(), before)

    def test_wrong_otp_records_access_attempt(self):
        from axes.models import AccessAttempt

        email = "axesotp@example.com"
        u = User(
            email=email,
            username="axesotpu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        create_challenge(email, EmailLoginChallenge.PURPOSE_LOGIN)
        before = AccessAttempt.objects.count()
        r = self._json_post(
            "sp_email_otp_verify",
            {
                "email": email,
                "code": "000000",
                "purpose": EmailLoginChallenge.PURPOSE_LOGIN,
            },
        )
        self.assertFalse(r.json().get("ok"))
        self.assertGreater(AccessAttempt.objects.count(), before)

    def test_password_reset_invalidates_sessions(self):
        from user_sessions.models import Session

        u = User(
            email="flush@example.com",
            username="flushu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        Session.objects.create(
            session_key="flushsess001",
            user_id=u.pk,
            expire_date=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(Session.objects.filter(user_id=u.pk).exists())
        set_password_and_revoke_trust(u, "NewerComplexPass!999")
        self.assertFalse(Session.objects.filter(user_id=u.pk).exists())

    def test_reset_otp_cannot_authenticate_via_otp_verify(self):
        email = "resetotp@example.com"
        u = User(
            email=email,
            username="resetotpu",
            email_verified_at=timezone.now(),
        )
        u.set_password("ComplexPass!234")
        u.save()
        _ch, code = create_challenge(email, EmailLoginChallenge.PURPOSE_RESET)
        r = self._json_post(
            "sp_email_otp_verify",
            {
                "email": email,
                "code": code,
                "purpose": EmailLoginChallenge.PURPOSE_RESET,
            },
        )
        data = r.json()
        self.assertFalse(data.get("ok"))
        self.assertEqual(data.get("field"), "code")
        self.assertNotIn("redirect", data)
        self.assertNotIn("_auth_user_id", self.client.session)

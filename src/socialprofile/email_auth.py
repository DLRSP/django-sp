"""Email password / OTP / trusted-device helpers (feature-flagged).

Distinct from django_otp TOTP/StaticDevice MFA. Never fuzzy-binds Party.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from datetime import timedelta
from typing import Any, MutableMapping

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

LOGGER = logging.getLogger("socialprofile.email_auth")

ASSOCIATE_BY_EMAIL = "social_core.pipeline.social_auth.associate_by_email"
EMAIL_AUTH_BACKEND = "social_core.backends.email.EmailAuth"
TRUST_COOKIE = "sp_trusted_device"
OTP_TTL_MINUTES = 10
OTP_MAX_ATTEMPTS = 5
TRUST_DAYS = 30
SEND_RATE_WINDOW = timedelta(minutes=15)
SEND_RATE_MAX = 5


def email_auth_enabled() -> bool:
    return bool(
        getattr(settings, "SP_EMAIL_PASSWORD_LOGIN", False)
        or getattr(settings, "SP_EMAIL_OTP_LOGIN", False)
        or getattr(settings, "SP_TRUSTED_DEVICE", False)
    )


def password_login_enabled() -> bool:
    return bool(getattr(settings, "SP_EMAIL_PASSWORD_LOGIN", False))


def otp_login_enabled() -> bool:
    return bool(getattr(settings, "SP_EMAIL_OTP_LOGIN", False))


def trusted_device_enabled() -> bool:
    return bool(getattr(settings, "SP_TRUSTED_DEVICE", False))


def email_auth_template_context(request: HttpRequest | None = None) -> dict[str, Any]:
    """Flags + one-shot flash panel/email for the select / login templates."""
    ctx: dict[str, Any] = {
        "sp_email_password_login": password_login_enabled(),
        "sp_email_otp_login": otp_login_enabled(),
        "sp_trusted_device": trusted_device_enabled(),
    }
    if request is None:
        return ctx
    session = getattr(request, "session", None)
    if session is None:
        return ctx
    panel = session.pop("sp_email_flash_panel", None)
    email = session.pop("sp_email_flash_email", "")
    purpose = session.pop("sp_email_flash_purpose", None)
    if panel:
        ctx["sp_email_flash_panel"] = panel
    if email:
        ctx["sp_email_flash_email"] = email
    if purpose:
        ctx["sp_email_flash_purpose"] = purpose
    return ctx


def apply_email_auth_security_overlays(ns: MutableMapping[str, Any]) -> None:
    """When any email-auth flag is True, neutralize ATO defaults and widen Axes keys."""
    flags = (
        bool(ns.get("SP_EMAIL_PASSWORD_LOGIN", False))
        or bool(ns.get("SP_EMAIL_OTP_LOGIN", False))
        or bool(ns.get("SP_TRUSTED_DEVICE", False))
    )
    if not flags:
        return

    pipeline = list(ns.get("SOCIAL_AUTH_PIPELINE") or ())
    if ASSOCIATE_BY_EMAIL in pipeline:
        ns["SOCIAL_AUTH_PIPELINE"] = tuple(
            s for s in pipeline if s != ASSOCIATE_BY_EMAIL
        )

    backends = list(ns.get("AUTHENTICATION_BACKENDS") or ())
    if EMAIL_AUTH_BACKEND in backends:
        ns["AUTHENTICATION_BACKENDS"] = tuple(
            b for b in backends if b != EMAIL_AUTH_BACKEND
        )

    # Axes: email/username + IP for lockout (beyond IP-only default).
    ns["AXES_LOCKOUT_PARAMETERS"] = [
        ["username", "ip_address"],
        ["ip_address"],
    ]


def normalize_email(email: str) -> str:
    return get_user_model().objects.normalize_email((email or "").strip())


def _pepper() -> bytes:
    return settings.SECRET_KEY.encode("utf-8")


def hash_secret(raw: str, *, salt: str = "") -> str:
    msg = f"{salt}:{raw}".encode("utf-8")
    return hmac.new(_pepper(), msg, hashlib.sha256).hexdigest()


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_challenge(email: str, purpose: str, *, ip: str = ""):
    from socialprofile.models import EmailLoginChallenge

    email_n = normalize_email(email)
    if not _allow_send(email_n, ip):
        return None, None

    code = generate_otp()
    salt = secrets.token_hex(8)
    now = timezone.now()
    EmailLoginChallenge.objects.filter(
        email=email_n, purpose=purpose, consumed_at__isnull=True
    ).update(consumed_at=now)

    challenge = EmailLoginChallenge.objects.create(
        email=email_n,
        purpose=purpose,
        code_hash=hash_secret(code, salt=salt),
        salt=salt,
        expires_at=now + timedelta(minutes=OTP_TTL_MINUTES),
        request_ip=ip[:64] if ip else "",
    )
    return challenge, code


def _allow_send(email: str, ip: str) -> bool:
    from socialprofile.models import EmailLoginChallenge

    since = timezone.now() - SEND_RATE_WINDOW
    qs = EmailLoginChallenge.objects.filter(created_at__gte=since)
    if qs.filter(email=email).count() >= SEND_RATE_MAX:
        return False
    if ip and qs.filter(request_ip=ip).count() >= SEND_RATE_MAX * 3:
        return False
    return True


def verify_challenge(email: str, code: str, purpose: str):
    from socialprofile.models import EmailLoginChallenge

    email_n = normalize_email(email)
    now = timezone.now()
    challenge = (
        EmailLoginChallenge.objects.filter(
            email=email_n,
            purpose=purpose,
            consumed_at__isnull=True,
            expires_at__gte=now,
        )
        .order_by("-created_at")
        .first()
    )
    if challenge is None:
        return None
    if challenge.attempt_count >= OTP_MAX_ATTEMPTS:
        return None
    challenge.attempt_count += 1
    challenge.save(update_fields=["attempt_count"])
    expected = hash_secret(code.strip(), salt=challenge.salt)
    if not hmac.compare_digest(expected, challenge.code_hash):
        return None
    challenge.consumed_at = now
    challenge.save(update_fields=["consumed_at"])
    return challenge


def send_otp_mail(email: str, code: str) -> None:
    subject = str(_("Your verification code"))
    body = str(
        _(
            "Your verification code is: %(code)s\n"
            "It expires in a few minutes.\n"
            "If you did not request this, ignore this email.\n"
        )
    ) % {"code": code}
    send_mail(
        subject,
        body,
        getattr(settings, "DEFAULT_FROM_EMAIL", None),
        [email],
        fail_silently=True,
    )


def send_reset_mail(email: str, code: str) -> None:
    subject = str(_("Password reset verification"))
    body = str(
        _(
            "Your password reset code is: %(code)s\n"
            "It expires in a few minutes.\n"
            "If you did not request this, ignore this email.\n"
        )
    ) % {"code": code}
    send_mail(
        subject,
        body,
        getattr(settings, "DEFAULT_FROM_EMAIL", None),
        [email],
        fail_silently=True,
    )


def find_user_by_email(email: str):
    User = get_user_model()
    email_n = normalize_email(email)
    return User.objects.filter(email__iexact=email_n, is_active=True).first()


def user_email_verified(user) -> bool:
    return bool(getattr(user, "email_verified_at", None))


def mark_email_verified(user) -> None:
    if getattr(user, "email_verified_at", None):
        return
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified_at"])


def issue_trusted_device(
    user, request: HttpRequest, response: HttpResponse
) -> None:
    if not trusted_device_enabled():
        return
    from socialprofile.models import TrustedDevice

    selector = secrets.token_urlsafe(16)
    raw = secrets.token_urlsafe(32)
    now = timezone.now()
    TrustedDevice.objects.create(
        user=user,
        selector=selector,
        token_hash=hash_secret(raw, salt=selector),
        expires_at=now + timedelta(days=TRUST_DAYS),
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:256],
    )
    secure = not bool(getattr(settings, "DEBUG", True))
    response.set_cookie(
        TRUST_COOKIE,
        f"{selector}:{raw}",
        max_age=TRUST_DAYS * 24 * 3600,
        httponly=True,
        secure=secure,
        samesite="Lax",
        path="/",
    )


def lookup_trusted_device(request: HttpRequest, user) -> bool:
    if not trusted_device_enabled():
        return False
    from socialprofile.models import TrustedDevice

    raw_cookie = request.COOKIES.get(TRUST_COOKIE) or ""
    if ":" not in raw_cookie:
        return False
    selector, raw = raw_cookie.split(":", 1)
    now = timezone.now()
    device = TrustedDevice.objects.filter(
        user=user,
        selector=selector,
        revoked_at__isnull=True,
        expires_at__gte=now,
    ).first()
    if device is None:
        return False
    expected = hash_secret(raw, salt=selector)
    if not hmac.compare_digest(expected, device.token_hash):
        return False
    device.last_used_at = now
    device.save(update_fields=["last_used_at"])
    return True


def revoke_trusted_devices(user) -> int:
    from socialprofile.models import TrustedDevice

    now = timezone.now()
    return TrustedDevice.objects.filter(
        user=user, revoked_at__isnull=True
    ).update(revoked_at=now)


def register_user(email: str, password: str):
    """Create or continue email registration; anti-enum response stays identical.

    Unverified existing rows may adopt the new password (mailbox still unproven).
    Verified accounts never change password here.
    """
    User = get_user_model()
    email_n = normalize_email(email)
    validate_password(password)

    existing = User.objects.filter(email__iexact=email_n).first()
    if existing:
        if getattr(existing, "email_verified_at", None) is None:
            validate_password(password, user=existing)
            existing.set_password(password)
            existing.save(update_fields=["password"])
        return existing, False

    base_username = email_n.split("@")[0][:20] or "user"
    username = base_username
    n = 0
    while User.objects.filter(username=username).exists():
        n += 1
        username = f"{base_username}{n}"[:30]

    with transaction.atomic():
        user = User(
            email=email_n,
            username=username,
            is_active=True,
            email_verified_at=None,
        )
        user.set_password(password)
        user.save()
    return user, True


def set_password_and_revoke_trust(user, password: str) -> None:
    validate_password(password, user=user)
    user.set_password(password)
    user.save(update_fields=["password"])
    revoke_trusted_devices(user)
    invalidate_user_sessions(user)


def invalidate_user_sessions(user) -> int:
    """Drop server-side sessions for ``user`` after password change/reset."""
    try:
        from user_sessions.models import Session
    except ImportError:
        return 0
    deleted, _ = Session.objects.filter(user_id=user.pk).delete()
    return int(deleted)


def axes_credentials(username: str) -> dict:
    return {"username": (username or "").strip()}


def axes_is_allowed(request: HttpRequest, username: str) -> bool:
    try:
        from axes.handlers.proxy import AxesProxyHandler
    except ImportError:
        return True
    return bool(
        AxesProxyHandler.is_allowed(request, axes_credentials(username))
    )


def axes_record_failure(request: HttpRequest, username: str) -> None:
    """Record a failed email-auth attempt for Axes (OTP/reset paths)."""
    from django.contrib.auth.signals import user_login_failed

    user_login_failed.send(
        sender=__name__,
        credentials=axes_credentials(username),
        request=request,
    )


def client_ip(request: HttpRequest) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or ""


GENERIC_OK = _("If an account exists for that email, we sent instructions.")
GENERIC_AUTH_FAIL = _("Invalid email or password.")
GENERIC_OTP_FAIL = _("Invalid or expired verification code.")

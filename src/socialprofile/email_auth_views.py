"""HTTP endpoints for email password / OTP / reset (404 when flags off)."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from socialprofile import email_auth as ea
from socialprofile.models import EmailLoginChallenge
from socialprofile.views import SelectAuthView

LOGGER = logging.getLogger("socialprofile.email_auth_views")

SESSION_PENDING_USER = "sp_email_pending_user_id"
SESSION_PENDING_TRUST = "sp_email_pending_trust"
SESSION_FLASH_PANEL = "sp_email_flash_panel"
SESSION_FLASH_EMAIL = "sp_email_flash_email"


def _require_any_flag():
    if not ea.email_auth_enabled():
        raise Http404()


def _safe_next(request) -> str:
    return SelectAuthView._safe_next_url(
        request.POST.get("next") or request.GET.get("next")
    )


def _wants_json(request) -> bool:
    accept = (request.headers.get("Accept") or "").lower()
    if "application/json" in accept and "text/html" not in accept:
        return True
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _select_url() -> str:
    return reverse("sp_select_page")


def _flash(request, panel: str | None = None, email: str = "") -> None:
    if panel:
        request.session[SESSION_FLASH_PANEL] = panel
    if email:
        request.session[SESSION_FLASH_EMAIL] = ea.normalize_email(email)


def _notify(request, *, ok: bool, detail: str, level: str = "info") -> None:
    """Toast when sweetify is available; otherwise django messages (never both)."""
    try:
        import sweetify

        icon = (
            "success"
            if ok and level == "success"
            else ("error" if not ok else "info")
        )
        sweetify.toast(request, detail, icon=icon, timer=4500)
        return
    except Exception:
        LOGGER.debug("sweetify unavailable", exc_info=True)

    if ok:
        if level == "success":
            messages.success(request, detail)
        else:
            messages.info(request, detail)
    else:
        messages.error(request, detail)


def _json_payload(
    *,
    ok: bool,
    detail: str,
    next_step: str | None = None,
    field: str | None = None,
    redirect_to: str | None = None,
    level: str = "info",
    purpose: str | None = None,
) -> dict:
    payload = {"ok": ok, "detail": detail, "level": level}
    if next_step:
        payload["next_step"] = next_step
    if field:
        payload["field"] = field
    if redirect_to:
        payload["redirect"] = redirect_to
    if purpose:
        payload["purpose"] = purpose
    return payload


def _respond(
    request,
    *,
    ok: bool = True,
    detail: str = "",
    next_step: str | None = None,
    redirect_to: str | None = None,
    email: str = "",
    level: str = "info",
    field: str | None = None,
    purpose: str | None = None,
):
    """
    Message channels:
    - field errors (password/code/email) → JSON field or redirect+panel (no toast)
    - status (code sent, signed in) → toast / messages
    Browser without JS → redirect; with XHR → JSON (no full reload).
    """
    detail = detail or str(ea.GENERIC_OK)
    if _wants_json(request):
        return JsonResponse(
            _json_payload(
                ok=ok,
                detail=detail,
                next_step=next_step,
                field=field,
                redirect_to=redirect_to,
                level=level,
                purpose=purpose,
            )
        )

    # Field-level: keep user on the form panel; surface via messages only if no JS
    if field and not ok:
        messages.error(request, detail)
    elif not field:
        _notify(request, ok=ok, detail=detail, level=level)

    if next_step:
        _flash(request, next_step, email)
        if purpose:
            request.session["sp_email_flash_purpose"] = purpose

    return redirect(redirect_to or _select_url())


def _login_response(
    request, user, *, next_url: str, remember: bool, detail: str
):
    """Authenticate session; JSON clients get redirect URL without full HTML round-trip."""
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    if _wants_json(request):
        response = JsonResponse(
            _json_payload(
                ok=True,
                detail=detail,
                redirect_to=next_url,
                level="success",
            )
        )
        if remember and ea.trusted_device_enabled():
            ea.issue_trusted_device(user, request, response)
        return response

    response = redirect(next_url)
    if remember and ea.trusted_device_enabled():
        ea.issue_trusted_device(user, request, response)
    _notify(request, ok=True, detail=detail, level="success")
    return response


@require_POST
def email_register(request):
    _require_any_flag()
    if not ea.password_login_enabled():
        raise Http404()
    email = request.POST.get("email", "")
    password = request.POST.get("password", "")
    password_confirm = request.POST.get("password_confirm", "")
    # Honeypot: filled ⇒ pretend success (anti-enum / anti-bot), do not create.
    if (request.POST.get("company") or "").strip():
        return _respond(
            request,
            ok=True,
            detail=str(_("Check your email for a verification code.")),
            next_step="otp",
            email=email,
            level="success",
        )
    if password != password_confirm:
        return _respond(
            request,
            ok=False,
            detail=str(_("Passwords do not match.")),
            next_step="register",
            email=email,
            field="password_confirm",
            level="error",
        )
    ip = ea.client_ip(request)
    try:
        user, created = ea.register_user(email, password)
    except ValidationError as exc:
        detail = (
            " ".join(exc.messages)
            if getattr(exc, "messages", None)
            else str(_("Password does not meet requirements."))
        )
        return _respond(
            request,
            ok=False,
            detail=detail,
            next_step="register",
            email=email,
            field="password",
            level="error",
        )
    except Exception:
        LOGGER.exception("email_register failed")
        return _respond(
            request,
            ok=False,
            detail=str(_("Could not create the account. Please try again.")),
            next_step="register",
            email=email,
            field="email",
            level="error",
        )

    # Anti-enumeration: existing email gets the same success UX; no "already registered".
    if created or not ea.user_email_verified(user):
        challenge, code = ea.create_challenge(
            email, EmailLoginChallenge.PURPOSE_REGISTER, ip=ip
        )
        if challenge and code:
            ea.send_otp_mail(ea.normalize_email(email), code)
    return _respond(
        request,
        ok=True,
        detail=str(_("Check your email for a verification code.")),
        next_step="otp",
        email=email,
        level="success",
        purpose=EmailLoginChallenge.PURPOSE_REGISTER,
    )


@require_POST
def email_login(request):
    _require_any_flag()
    if not ea.password_login_enabled():
        raise Http404()
    email = request.POST.get("email", "")
    password = request.POST.get("password", "")
    remember = request.POST.get("remember_device") in (
        "1",
        "on",
        "true",
        "True",
    )
    next_url = _safe_next(request)
    username_key = ea.normalize_email(email) or email
    if not ea.axes_is_allowed(request, username_key):
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_AUTH_FAIL),
            next_step="login",
            email=email,
            field="password",
        )
    user = ea.find_user_by_email(email)
    authed = None
    called_authenticate = False
    if user is not None:
        called_authenticate = True
        authed = authenticate(
            request, username=user.username, password=password
        )
        if authed is None:
            authed = authenticate(request, username=email, password=password)

    if authed is None:
        if not called_authenticate:
            ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_AUTH_FAIL),
            next_step="login",
            email=email,
            field="password",
        )

    if not ea.user_email_verified(authed):
        ip = ea.client_ip(request)
        challenge, code = ea.create_challenge(
            authed.email, EmailLoginChallenge.PURPOSE_REGISTER, ip=ip
        )
        if challenge and code:
            ea.send_otp_mail(authed.email, code)
        return _respond(
            request,
            ok=False,
            detail=str(_("Verify your email before signing in.")),
            next_step="otp",
            email=authed.email,
            level="info",
            purpose=EmailLoginChallenge.PURPOSE_REGISTER,
        )

    needs_otp = ea.otp_login_enabled() and not ea.lookup_trusted_device(
        request, authed
    )
    if needs_otp:
        request.session[SESSION_PENDING_USER] = authed.pk
        request.session[SESSION_PENDING_TRUST] = bool(remember)
        ip = ea.client_ip(request)
        challenge, code = ea.create_challenge(
            authed.email, EmailLoginChallenge.PURPOSE_LOGIN, ip=ip
        )
        if challenge and code:
            ea.send_otp_mail(authed.email, code)
        return _respond(
            request,
            ok=True,
            detail=str(_("Check your email for a verification code.")),
            next_step="otp",
            email=authed.email,
            level="success",
            purpose=EmailLoginChallenge.PURPOSE_LOGIN,
        )

    return _login_response(
        request,
        authed,
        next_url=next_url,
        remember=remember,
        detail=str(_("Signed in successfully.")),
    )


@require_POST
def email_otp_request(request):
    _require_any_flag()
    if not ea.otp_login_enabled():
        raise Http404()
    email = request.POST.get("email", "")
    username_key = ea.normalize_email(email) or email
    if not ea.axes_is_allowed(request, username_key):
        ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=True,
            detail=str(ea.GENERIC_OK),
            next_step="otp",
            email=email,
            level="success",
            purpose=EmailLoginChallenge.PURPOSE_LOGIN,
        )
    ip = ea.client_ip(request)
    user = ea.find_user_by_email(email)
    if user is not None:
        challenge, code = ea.create_challenge(
            email, EmailLoginChallenge.PURPOSE_LOGIN, ip=ip
        )
        if challenge and code:
            ea.send_otp_mail(user.email, code)
        elif challenge is None:
            ea.axes_record_failure(request, username_key)
    else:
        challenge, _code = ea.create_challenge(
            email, EmailLoginChallenge.PURPOSE_LOGIN, ip=ip
        )
        if challenge is None:
            ea.axes_record_failure(request, username_key)
    return _respond(
        request,
        ok=True,
        detail=str(ea.GENERIC_OK),
        next_step="otp",
        email=email,
        level="success",
        purpose=EmailLoginChallenge.PURPOSE_LOGIN,
    )


@require_POST
def email_otp_verify(request):
    _require_any_flag()
    if not ea.otp_login_enabled() and not ea.password_login_enabled():
        raise Http404()
    email = request.POST.get("email", "")
    code = request.POST.get("code", "")
    remember = request.POST.get("remember_device") in (
        "1",
        "on",
        "true",
        "True",
    )
    next_url = _safe_next(request)
    purpose = request.POST.get("purpose") or EmailLoginChallenge.PURPOSE_LOGIN
    verify_purposes = (
        EmailLoginChallenge.PURPOSE_LOGIN,
        EmailLoginChallenge.PURPOSE_REGISTER,
    )
    username_key = ea.normalize_email(email) or email
    if purpose not in verify_purposes:
        ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_OTP_FAIL),
            next_step="otp",
            email=email,
            field="code",
        )
    if not ea.axes_is_allowed(request, username_key):
        ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_OTP_FAIL),
            next_step="otp",
            email=email,
            field="code",
        )

    pending_id = request.session.get(SESSION_PENDING_USER)
    if pending_id and purpose == EmailLoginChallenge.PURPOSE_LOGIN:
        User = get_user_model()
        try:
            pending = User.objects.get(pk=pending_id)
        except User.DoesNotExist:
            pending = None
        email = pending.email if pending else email
        username_key = ea.normalize_email(email) or email

    challenge = ea.verify_challenge(email, code, purpose)
    if challenge is None:
        ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_OTP_FAIL),
            next_step="otp",
            email=email,
            field="code",
        )

    from django.conf import settings as dj_settings

    welcome = getattr(
        dj_settings, "SOCIAL_AUTH_NEW_USER_REDIRECT_URL", "/sp/new-profile/"
    )

    if purpose == EmailLoginChallenge.PURPOSE_REGISTER:
        user = ea.find_user_by_email(email)
        if user is None:
            return _respond(
                request,
                ok=False,
                detail=str(ea.GENERIC_OTP_FAIL),
                next_step="otp",
                email=email,
                field="code",
            )
        ea.mark_email_verified(user)
        request.session.pop(SESSION_PENDING_USER, None)
        return _login_response(
            request,
            user,
            next_url=welcome,
            remember=remember,
            detail=str(_("Email verified. Welcome!")),
        )

    if purpose != EmailLoginChallenge.PURPOSE_LOGIN:
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_OTP_FAIL),
            next_step="otp",
            email=email,
            field="code",
        )

    user = ea.find_user_by_email(email)
    if user is None:
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_OTP_FAIL),
            next_step="otp",
            email=email,
            field="code",
        )
    was_unverified = not ea.user_email_verified(user)
    ea.mark_email_verified(user)
    remember = remember or bool(
        request.session.pop(SESSION_PENDING_TRUST, False)
    )
    request.session.pop(SESSION_PENDING_USER, None)
    dest = welcome if was_unverified else next_url
    return _login_response(
        request,
        user,
        next_url=dest,
        remember=remember,
        detail=str(_("Signed in successfully.")),
    )


@require_POST
def email_password_reset(request):
    _require_any_flag()
    if not ea.password_login_enabled():
        raise Http404()
    email = request.POST.get("email", "")
    username_key = ea.normalize_email(email) or email
    if not ea.axes_is_allowed(request, username_key):
        ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=True,
            detail=str(ea.GENERIC_OK),
            next_step="reset",
            email=email,
            level="success",
        )
    ip = ea.client_ip(request)
    user = ea.find_user_by_email(email)
    if user is not None:
        challenge, code = ea.create_challenge(
            email, EmailLoginChallenge.PURPOSE_RESET, ip=ip
        )
        if challenge and code:
            ea.send_reset_mail(user.email, code)
        elif challenge is None:
            ea.axes_record_failure(request, username_key)
    else:
        challenge, _code = ea.create_challenge(
            email, EmailLoginChallenge.PURPOSE_RESET, ip=ip
        )
        if challenge is None:
            ea.axes_record_failure(request, username_key)
    return _respond(
        request,
        ok=True,
        detail=str(ea.GENERIC_OK),
        next_step="reset",
        email=email,
        level="success",
    )


@require_POST
def email_password_reset_confirm(request):
    _require_any_flag()
    if not ea.password_login_enabled():
        raise Http404()
    email = request.POST.get("email", "")
    code = request.POST.get("code", "")
    password = request.POST.get("password", "")
    username_key = ea.normalize_email(email) or email
    if not ea.axes_is_allowed(request, username_key):
        ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_OTP_FAIL),
            next_step="reset",
            email=email,
            field="code",
        )
    challenge = ea.verify_challenge(
        email, code, EmailLoginChallenge.PURPOSE_RESET
    )
    if challenge is None:
        ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_OTP_FAIL),
            next_step="reset",
            email=email,
            field="code",
        )
    user = ea.find_user_by_email(email)
    if user is None:
        ea.axes_record_failure(request, username_key)
        return _respond(
            request,
            ok=False,
            detail=str(ea.GENERIC_OTP_FAIL),
            next_step="reset",
            email=email,
            field="code",
        )
    try:
        ea.set_password_and_revoke_trust(user, password)
    except ValidationError as exc:
        detail = (
            " ".join(exc.messages)
            if getattr(exc, "messages", None)
            else str(_("Password does not meet requirements."))
        )
        return _respond(
            request,
            ok=False,
            detail=detail,
            next_step="reset",
            email=email,
            field="password",
        )
    ea.mark_email_verified(user)
    return _respond(
        request,
        ok=True,
        detail=str(_("Password updated. You can sign in.")),
        next_step="login",
        email=email,
        level="success",
    )


@ensure_csrf_cookie
@require_http_methods(["GET"])
def email_auth_status(_request):
    """Lightweight flag probe for templates/tests."""
    if not ea.email_auth_enabled():
        raise Http404()
    return JsonResponse(
        {
            "password": ea.password_login_enabled(),
            "otp": ea.otp_login_enabled(),
            "trusted_device": ea.trusted_device_enabled(),
        }
    )

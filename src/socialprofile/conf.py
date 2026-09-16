"""Resolve django-sp settings onto the project namespace.

Call at the end of consumer ``settings.py`` (after ``DEBUG`` and HTTPS/proxy
headers are defined)::

    from socialprofile.conf import apply_sp_defaults
    apply_sp_defaults(globals())

Explicit project settings always win. ``APP_CONFIG["socialprofile"]`` may supply
site-specific values (for example ``CSRF_TRUSTED_ORIGINS`` hostnames).
"""

from __future__ import annotations

from typing import Any, MutableMapping

from . import defaults

APP_KEY = "socialprofile"
_UNSET = object()


def _has(ns: MutableMapping[str, Any], name: str) -> bool:
    return name in ns


def _get(ns: MutableMapping[str, Any], name: str, default=_UNSET):
    if default is _UNSET:
        return ns.get(name)
    return ns.get(name, default)


def _setdefault(ns: MutableMapping[str, Any], name: str, value) -> None:
    if not _has(ns, name):
        ns[name] = value


def _app_config(ns: MutableMapping[str, Any]) -> dict[str, Any]:
    raw = _get(ns, "APP_CONFIG", {}) or {}
    block = raw.get(APP_KEY)
    return dict(block) if isinstance(block, dict) else {}


def _is_production(ns: MutableMapping[str, Any]) -> bool:
    return not bool(_get(ns, "DEBUG", True))


def _proxy_indicates_https(ns: MutableMapping[str, Any]) -> bool:
    header = _get(ns, "SECURE_PROXY_SSL_HEADER")
    if not header or not isinstance(header, (tuple, list)) or len(header) != 2:
        return False
    return header[1] == "https"


def apply_sp_defaults(settings: MutableMapping[str, Any]) -> None:
    """Apply django-sp defaults without overwriting explicit project values."""
    app_cfg = _app_config(settings)

    # Core login / redirect paths (consumers may override prefix via APP_CONFIG).
    sp_prefix = app_cfg.get("url_prefix", "/sp")
    if not sp_prefix.startswith("/"):
        sp_prefix = f"/{sp_prefix}"
    sp_prefix = sp_prefix.rstrip("/") or "/sp"

    _setdefault(settings, "LOGIN_URL", f"{sp_prefix}/select/")
    _setdefault(settings, "LOGIN_ERROR_URL", f"{sp_prefix}/select/")
    _setdefault(settings, "LOGIN_REDIRECT_URL", f"{sp_prefix}/")
    _setdefault(settings, "DEFAULT_RETURNTO_PATH", f"{sp_prefix}/")

    _setdefault(settings, "SOCIAL_AUTH_LOGIN_REDIRECT_URL", f"{sp_prefix}/")
    _setdefault(settings, "SOCIAL_AUTH_LOGIN_ERROR_URL", f"{sp_prefix}/login-error/")
    _setdefault(settings, "SOCIAL_AUTH_LOGIN_URL", f"{sp_prefix}/select/")
    _setdefault(
        settings,
        "SOCIAL_AUTH_NEW_USER_REDIRECT_URL",
        f"{sp_prefix}/new-profile/",
    )
    _setdefault(
        settings,
        "SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL",
        f"{sp_prefix}/new-association/",
    )

    _setdefault(settings, "AUTH_USER_MODEL", "socialprofile.socialprofile")
    _setdefault(settings, "SOCIAL_AUTH_USER_MODEL", "socialprofile.socialprofile")
    _setdefault(settings, "SOCIAL_AUTH_RAISE_EXCEPTIONS", True)
    _setdefault(
        settings,
        "SOCIAL_AUTH_STRATEGY",
        "social_django.strategy.DjangoStrategy",
    )
    _setdefault(settings, "SOCIAL_AUTH_STORAGE", "social_django.models.DjangoStorage")
    _setdefault(settings, "SOCIAL_AUTH_ACTIVE_USERS_FILTER", {"is_active": True})
    _setdefault(settings, "SOCIAL_AUTH_ALWAYS_ASSOCIATE", True)
    _setdefault(
        settings,
        "SOCIAL_AUTH_PROTECTED_USER_FIELDS",
        ["username", "email", "first_name", "last_name"],
    )
    _setdefault(settings, "SOCIAL_AUTH_REVOKE_TOKENS_ON_DISCONNECT", True)
    _setdefault(settings, "SP_SET_USERNAME", True)

    _setdefault(settings, "SOCIAL_AUTH_PIPELINE", defaults.DEFAULT_SOCIAL_AUTH_PIPELINE)
    _setdefault(
        settings,
        "AUTHENTICATION_BACKENDS",
        defaults.DEFAULT_AUTHENTICATION_BACKENDS,
    )

    oauth2 = dict(defaults.DEFAULT_OAUTH2_PROVIDER)
    oauth2.update(_get(settings, "OAUTH2_PROVIDER", {}) or {})
    if "OAUTH2_PROVIDER" not in settings:
        settings["OAUTH2_PROVIDER"] = oauth2
    else:
        settings["OAUTH2_PROVIDER"].setdefault(
            "OAUTH2_VALIDATOR_CLASS",
            defaults.DEFAULT_OAUTH2_PROVIDER["OAUTH2_VALIDATOR_CLASS"],
        )

    for key, value in defaults.DEFAULT_AXES_BEHIND_PROXY.items():
        _setdefault(settings, key, value)

    # social-auth-app-django 6.0.0+ builds OAuth redirect URIs from this flag.
    if _is_production(settings) and _proxy_indicates_https(settings):
        _setdefault(settings, "USE_X_FORWARDED_HOST", True)
        _setdefault(settings, "SOCIAL_AUTH_REDIRECT_IS_HTTPS", True)

    # OAuth complete is a top-level GET from the IdP. SameSite=Strict drops the
    # session cookie on return (AuthStateMissing / 500). None diverges fleet-wide.
    # Canonical shared value: Lax (CSRF may remain Strict for same-site POST begin).
    _ensure_session_samesite_lax(settings)

    trusted = app_cfg.get("csrf_trusted_origins")
    if trusted and not _has(settings, "CSRF_TRUSTED_ORIGINS"):
        settings["CSRF_TRUSTED_ORIGINS"] = list(trusted)


def _ensure_session_samesite_lax(settings: MutableMapping[str, Any]) -> None:
    """Force SESSION_COOKIE_SAMESITE=Lax when unset, None, or Strict."""
    if not _has(settings, "SESSION_COOKIE_SAMESITE"):
        settings["SESSION_COOKIE_SAMESITE"] = "Lax"
        return
    current = settings["SESSION_COOKIE_SAMESITE"]
    if current is None:
        settings["SESSION_COOKIE_SAMESITE"] = "Lax"
        return
    if isinstance(current, str) and current.lower() == "strict":
        settings["SESSION_COOKIE_SAMESITE"] = "Lax"

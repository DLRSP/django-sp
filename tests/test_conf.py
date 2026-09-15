"""Tests for socialprofile.conf.apply_sp_defaults."""

from socialprofile.conf import apply_sp_defaults


def test_apply_sp_defaults_sets_core_urls():
    settings = {}
    apply_sp_defaults(settings)
    assert settings["LOGIN_URL"] == "/sp/select/"
    assert settings["SOCIAL_AUTH_LOGIN_REDIRECT_URL"] == "/sp/"


def test_apply_sp_defaults_does_not_overwrite_explicit():
    settings = {"LOGIN_URL": "/custom/login/"}
    apply_sp_defaults(settings)
    assert settings["LOGIN_URL"] == "/custom/login/"


def test_apply_sp_defaults_https_redirect_in_production():
    settings = {
        "DEBUG": False,
        "SECURE_PROXY_SSL_HEADER": ("HTTP_X_FORWARDED_PROTO", "https"),
    }
    apply_sp_defaults(settings)
    assert settings["SOCIAL_AUTH_REDIRECT_IS_HTTPS"] is True
    assert settings["USE_X_FORWARDED_HOST"] is True


def test_apply_sp_defaults_skips_https_redirect_in_debug():
    settings = {
        "DEBUG": True,
        "SECURE_PROXY_SSL_HEADER": ("HTTP_X_FORWARDED_PROTO", "https"),
    }
    apply_sp_defaults(settings)
    assert "SOCIAL_AUTH_REDIRECT_IS_HTTPS" not in settings


def test_apply_sp_defaults_app_config_csrf_origins():
    settings = {
        "APP_CONFIG": {
            "socialprofile": {
                "csrf_trusted_origins": ["https://example.com"],
            }
        }
    }
    apply_sp_defaults(settings)
    assert settings["CSRF_TRUSTED_ORIGINS"] == ["https://example.com"]

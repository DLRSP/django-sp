"""Party dual-write pipeline — default off; opt-in when party installed."""
import pytest
from django.apps import apps
from django.conf import settings
from django.test import override_settings

from socialprofile.defaults import OPTIONAL_SOCIAL_AUTH_BACKENDS, PARTY_SYNC_PIPELINE_STEP
from socialprofile.party_sync import party_sync_enabled, sync_party_from_profile


def test_optional_provider_backends_listed():
    joined = " ".join(OPTIONAL_SOCIAL_AUTH_BACKENDS)
    assert "linkedin" in joined
    assert "discord" in joined
    assert "github" in joined


def test_party_sync_pipeline_step_constant():
    assert PARTY_SYNC_PIPELINE_STEP.endswith("sync_party_from_profile")


@pytest.mark.django_db
def test_party_sync_disabled_by_default():
    assert getattr(settings, "SP_PARTY_SYNC", False) is False or not party_sync_enabled()
    assert sync_party_from_profile(None, {}, user=None) is None


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
def test_party_sync_noops_without_party_app():
    if apps.is_installed("party"):
        pytest.skip("party installed in this env")
    assert party_sync_enabled() is False


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
def test_party_sync_writes_extid_when_party_installed():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ExternalIdentity, Party

    User = get_user_model()
    user = User.objects.create_user(
        username="syncuser",
        email="sync@example.com",
        password="x",
        first_name="Ada",
        last_name="Lovelace",
    )
    sync_party_from_profile(None, {}, user=user)
    ext = ExternalIdentity.objects.filter(
        namespace="socialprofile", scheme="user", value=str(user.pk), valid_to__isnull=True
    ).first()
    assert ext is not None
    assert Party.objects.filter(pk=ext.party_id).exists()
    assert ext.party.given_name == "Ada"


@pytest.mark.django_db
@override_settings(SP_PARTY_ADMIN_THIN=True)
def test_admin_thin_fieldsets_omit_provider_blocks():
    from socialprofile.admin import CustomUserAdmin
    from socialprofile.models import SocialProfile
    from django.contrib.admin.sites import AdminSite

    admin = CustomUserAdmin(SocialProfile, AdminSite())
    fieldsets = admin.get_fieldsets(request=None)
    labels = [fs[0] for fs in fieldsets]
    assert "Google" not in labels
    assert "Facebook" not in labels
    assert "Personal info" not in labels

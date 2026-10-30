"""Party dual-write pipeline — default off; opt-in when party installed."""

from unittest.mock import patch

import pytest
from django.apps import apps
from django.conf import settings
from django.test import override_settings

from socialprofile.defaults import (
    OPTIONAL_SOCIAL_AUTH_BACKENDS,
    PARTY_SYNC_PIPELINE_STEP,
)
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
    assert (
        getattr(settings, "SP_PARTY_SYNC", False) is False
        or not party_sync_enabled()
    )
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
        namespace="socialprofile",
        scheme="user",
        value=str(user.pk),
        valid_to__isnull=True,
    ).first()
    assert ext is not None
    assert Party.objects.filter(pk=ext.party_id).exists()
    assert ext.party.given_name == "Ada"


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
def test_party_sync_idempotent_second_pass():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ExternalIdentity, Party

    User = get_user_model()
    user = User.objects.create_user(
        username="idemuser",
        email="idem@example.com",
        password="x",
        first_name="Ida",
    )
    sync_party_from_profile(None, {}, user=user)
    sync_party_from_profile(None, {}, user=user)
    assert (
        ExternalIdentity.objects.filter(
            namespace="socialprofile",
            scheme="user",
            value=str(user.pk),
            valid_to__isnull=True,
        ).count()
        == 1
    )
    assert Party.objects.count() >= 1


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
def test_edited_by_user_blocks_party_name_overwrite():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ExternalIdentity

    User = get_user_model()
    user = User.objects.create_user(
        username="editguard",
        email="edit@example.com",
        password="x",
        first_name="Original",
        last_name="Name",
    )
    sync_party_from_profile(None, {}, user=user)
    ext = ExternalIdentity.objects.get(
        namespace="socialprofile",
        scheme="user",
        value=str(user.pk),
        valid_to__isnull=True,
    )
    party = ext.party
    party.given_name = "CRM"
    party.family_name = "Locked"
    party.save()
    user.first_name = "Provider"
    user.last_name = "Overwrite"
    user.edited_by_user = True
    user.save()
    sync_party_from_profile(None, {}, user=user)
    party.refresh_from_db()
    assert party.given_name == "CRM"
    assert party.family_name == "Locked"


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
def test_provider_uid_extid_and_no_consent():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ConsentRecord, ExternalIdentity
    from social_django.models import UserSocialAuth

    User = get_user_model()
    user = User.objects.create_user(
        username="provuser", email="prov@example.com", password="x"
    )
    UserSocialAuth.objects.create(
        user=user, provider="google-oauth2", uid="g-uid-99"
    )
    before = ConsentRecord.objects.count()
    sync_party_from_profile(None, {}, user=user)
    assert ExternalIdentity.objects.filter(
        namespace="socialprofile",
        scheme="google",
        value="g-uid-99",
        valid_to__isnull=True,
    ).exists()
    assert ConsentRecord.objects.count() == before


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True, SP_PARTY_MIRROR_LOGIN_EMAIL=False)
def test_login_email_not_mirrored_as_contact_point():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ContactPoint, ExternalIdentity

    User = get_user_model()
    user = User.objects.create_user(
        username="nomirror", email="keep@example.com", password="x"
    )
    sync_party_from_profile(None, {}, user=user)
    party = ExternalIdentity.objects.get(
        namespace="socialprofile",
        scheme="user",
        value=str(user.pk),
        valid_to__isnull=True,
    ).party
    assert not ContactPoint.objects.filter(
        party=party, channel="email"
    ).exists()


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
def test_sync_swallows_inner_errors():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(
        username="failopen", email="fail@example.com", password="x"
    )
    with patch(
        "socialprofile.party_sync._sync_user", side_effect=RuntimeError("boom")
    ):
        assert sync_party_from_profile(None, {}, user=user) is None


@pytest.mark.django_db
@override_settings(SP_PARTY_ADMIN_THIN=True)
def test_admin_thin_fieldsets_omit_provider_blocks():
    from django.contrib.admin.sites import AdminSite

    from socialprofile.admin import CustomUserAdmin
    from socialprofile.models import SocialProfile

    admin = CustomUserAdmin(SocialProfile, AdminSite())
    fieldsets = admin.get_fieldsets(request=None)
    labels = [fs[0] for fs in fieldsets]
    assert "Google" not in labels
    assert "Facebook" not in labels
    assert "Personal info" not in labels
    assert "gender" not in admin.get_list_display(request=None)
    assert "edited_by_google" not in admin.get_list_display(request=None)

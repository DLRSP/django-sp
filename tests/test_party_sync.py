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


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True, SP_PARTY_ADMIN_THIN=False)
def test_admin_full_fieldsets_when_thin_off_even_if_sync_on():
    """Sync alone must not demote AUTH fieldsets; thin flag is independent."""
    from django.contrib.admin.sites import AdminSite
    from django.contrib.auth import get_user_model

    from socialprofile.admin import CustomUserAdmin
    from socialprofile.models import SocialProfile

    User = get_user_model()
    existing = User.objects.create_user(
        username="fulladmin", email="fulladmin@example.com", password="x"
    )
    admin = CustomUserAdmin(SocialProfile, AdminSite())
    # UserAdmin returns add_fieldsets when obj is None; pass an existing user.
    labels = [fs[0] for fs in admin.get_fieldsets(request=None, obj=existing)]
    assert "Google" in labels
    assert "Personal info" in labels
    display = admin.get_list_display(request=None)
    assert "gender" in display
    assert "edited_by_google" in display


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=False, SP_PARTY_ADMIN_THIN=True)
def test_admin_thin_works_without_party_sync():
    from django.contrib.admin.sites import AdminSite
    from django.contrib.auth import get_user_model

    from socialprofile.admin import CustomUserAdmin
    from socialprofile.models import SocialProfile

    User = get_user_model()
    existing = User.objects.create_user(
        username="thinadmin", email="thinadmin@example.com", password="x"
    )
    admin = CustomUserAdmin(SocialProfile, AdminSite())
    assert (
        admin.get_list_display(request=None)
        == CustomUserAdmin.THIN_LIST_DISPLAY
    )
    labels = [fs[0] for fs in admin.get_fieldsets(request=None, obj=existing)]
    assert "Google" not in labels
    assert "Providers" not in labels
    # AUTH chrome must never advertise Contatti as a section title.
    flat = " ".join(str(x) for x in labels if x)
    assert "Contatti" not in flat
    assert "Contatti" not in " ".join(
        str(c) for c in admin.get_list_display(request=None)
    )


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
@pytest.mark.parametrize(
    "provider,uid,scheme",
    [
        ("google-oauth2", "g-uid-1", "google"),
        ("facebook", "fb-uid-1", "facebook"),
        ("twitter", "tw-uid-1", "twitter"),
        ("live", "live-uid-1", "live"),
        ("instagram", "ig-uid-1", "instagram"),
        ("linkedin-oauth2", "li-uid-1", "linkedin"),
        ("discord", "dc-uid-1", "discord"),
        ("github", "gh-uid-1", "github"),
    ],
)
def test_provider_uid_extid_matrix(provider, uid, scheme):
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ExternalIdentity
    from social_django.models import UserSocialAuth

    User = get_user_model()
    safe = scheme.replace("-", "")
    user = User.objects.create_user(
        username=f"prov_{safe}_{uid[:6]}",
        email=f"{safe}@example.com",
        password="x",
    )
    UserSocialAuth.objects.create(
        user=user,
        provider=provider,
        uid=uid,
        extra_data={
            "access_token": "secret-token-never-extid",
            "refresh_token": "r",
        },
    )
    sync_party_from_profile(None, {}, user=user)
    assert ExternalIdentity.objects.filter(
        namespace="socialprofile",
        scheme=scheme,
        value=uid,
        valid_to__isnull=True,
    ).exists()
    assert not ExternalIdentity.objects.filter(
        value="secret-token-never-extid"
    ).exists()
    assert not ExternalIdentity.objects.filter(value="r").exists()


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
def test_provider_extids_idempotent_across_core_providers():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ExternalIdentity
    from social_django.models import UserSocialAuth

    User = get_user_model()
    user = User.objects.create_user(
        username="multiprov", email="multi@example.com", password="x"
    )
    for provider, uid in (
        ("google-oauth2", "g-multi"),
        ("facebook", "fb-multi"),
        ("twitter", "tw-multi"),
        ("live", "live-multi"),
    ):
        UserSocialAuth.objects.create(user=user, provider=provider, uid=uid)
    sync_party_from_profile(None, {}, user=user)
    sync_party_from_profile(None, {}, user=user)
    for scheme, uid in (
        ("google", "g-multi"),
        ("facebook", "fb-multi"),
        ("twitter", "tw-multi"),
        ("live", "live-multi"),
    ):
        assert (
            ExternalIdentity.objects.filter(
                namespace="socialprofile",
                scheme=scheme,
                value=uid,
                valid_to__isnull=True,
            ).count()
            == 1
        )


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
def test_unlinked_optional_provider_leaves_no_extid():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ExternalIdentity

    User = get_user_model()
    user = User.objects.create_user(
        username="noprov", email="noprov@example.com", password="x"
    )
    sync_party_from_profile(None, {}, user=user)
    for scheme in ("linkedin", "discord", "github", "instagram"):
        assert not ExternalIdentity.objects.filter(
            namespace="socialprofile", scheme=scheme, valid_to__isnull=True
        ).exists()


def test_optional_providers_have_no_fat_socialprofile_columns():
    from socialprofile.models import SocialProfile

    field_names = {f.name for f in SocialProfile._meta.get_fields()}
    for name in (
        "linkedin_username",
        "linkedin_email",
        "discord_username",
        "discord_email",
        "github_username",
        "github_email",
    ):
        assert name not in field_names


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True)
@pytest.mark.parametrize(
    "evil_provider", ("user", "user-oauth2", "USER-OAuth2")
)
def test_reserved_user_provider_cannot_hijack_victim_extid(evil_provider):
    """IdP names that normalize to scheme ``user`` must never mint user ExtIds."""
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.models import ExternalIdentity, Party
    from social_django.models import UserSocialAuth

    User = get_user_model()
    suffix = evil_provider.lower().replace("-", "")[:12]
    # SocialProfileManager.create_user ignores username; set after save.
    attacker = User.objects.create_user(f"attacker-{suffix}@example.com", "x")
    attacker.username = f"attacker_{suffix}"
    attacker.save(update_fields=["username"])
    victim = User.objects.create_user(f"victim-{suffix}@example.com", "x")
    victim.username = f"victim_{suffix}"
    victim.save(update_fields=["username"])
    UserSocialAuth.objects.create(
        user=attacker,
        provider=evil_provider,
        uid=str(victim.pk),
    )
    sync_party_from_profile(None, {}, user=attacker)

    assert not ExternalIdentity.objects.filter(
        namespace="socialprofile",
        scheme="user",
        value=str(victim.pk),
        valid_to__isnull=True,
    ).exists()
    attacker_party = (
        ExternalIdentity.objects.filter(
            namespace="socialprofile",
            scheme="user",
            value=str(attacker.pk),
            valid_to__isnull=True,
        )
        .select_related("party")
        .get()
        .party
    )
    assert attacker_party.kind == Party.Kind.PERSON

    sync_party_from_profile(None, {}, user=victim)
    victim_ext = ExternalIdentity.objects.get(
        namespace="socialprofile",
        scheme="user",
        value=str(victim.pk),
        valid_to__isnull=True,
    )
    assert victim_ext.party_id != attacker_party.pk
    assert (
        ExternalIdentity.objects.filter(
            namespace="socialprofile",
            scheme="user",
            value=str(victim.pk),
            valid_to__isnull=True,
        ).count()
        == 1
    )


def test_provider_extid_scheme_rejects_reserved_and_unknown():
    from socialprofile.party_sync import _provider_extid_scheme

    assert _provider_extid_scheme("user") is None
    assert _provider_extid_scheme("user-oauth2") is None
    assert _provider_extid_scheme("") is None
    assert _provider_extid_scheme("totally-unknown-idp") is None
    assert _provider_extid_scheme("google-oauth2") == "google"
    assert _provider_extid_scheme("linkedin-oauth2") == "linkedin"

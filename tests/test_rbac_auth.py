"""AUTH-plane feature groups and AUTH vs CRM permission separation."""

from __future__ import annotations

import pytest
from django.apps import apps
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission
from django.test import override_settings

from socialprofile.rbac import AUTH_FEATURE_GROUPS, seed_auth_feature_groups


def _ensure_permissions(*app_labels: str) -> None:
    for label in app_labels:
        create_permissions(apps.get_app_config(label), verbosity=0)


@pytest.mark.django_db
def test_auth_feature_groups_seed_idempotent():
    _ensure_permissions(
        "socialprofile", "social_django", "user_sessions", "axes"
    )
    seed_auth_feature_groups()
    seed_auth_feature_groups()
    names = set(Group.objects.values_list("name", flat=True))
    for group_name in AUTH_FEATURE_GROUPS:
        assert group_name in names
    # AUTH seed never invents Italian Contatti group codes.
    assert "dlrsp:crm.contatti_view" not in names
    assert "dlrsp:auth.contatti_view" not in names
    for group_name in AUTH_FEATURE_GROUPS:
        assert group_name.startswith("dlrsp:auth.")


@pytest.mark.django_db
def test_auth_user_manage_group_has_socialprofile_change():
    _ensure_permissions("socialprofile")
    seed_auth_feature_groups()
    group = Group.objects.get(name="dlrsp:auth.user_manage")
    codenames = set(group.permissions.values_list("codename", flat=True))
    assert "change_socialprofile" in codenames
    assert "view_socialprofile" in codenames


@pytest.mark.django_db
def test_auth_user_manage_without_crm_cannot_mutate_party():
    """AUTH staff with user_manage alone must not hold Party CRM write perms."""
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model

    _ensure_permissions("socialprofile", "party")
    seed_auth_feature_groups()
    from party.rbac import seed_crm_feature_groups

    seed_crm_feature_groups()

    User = get_user_model()
    user = User.objects.create_user(
        username="authonly", email="authonly@example.com", password="x"
    )
    user.groups.add(Group.objects.get(name="dlrsp:auth.user_manage"))
    # Refresh permission cache after group assignment.
    user = User.objects.get(pk=user.pk)
    assert user.has_perm("socialprofile.change_socialprofile")
    assert not user.has_perm("party.change_party")
    assert not user.has_perm("party.add_contactpoint")
    assert not user.has_perm("party.change_externalidentity")
    assert not user.has_perm("party.add_partyaccount")


@pytest.mark.django_db
def test_contacts_view_can_read_party_but_not_mutate():
    if not apps.is_installed("party"):
        pytest.skip("django-party not installed")
    from django.contrib.auth import get_user_model
    from party.rbac import seed_crm_feature_groups

    _ensure_permissions("party")
    seed_crm_feature_groups()
    User = get_user_model()
    user = User.objects.create_user(
        username="crmview", email="crmview@example.com", password="x"
    )
    user.groups.add(Group.objects.get(name="dlrsp:crm.contacts_view"))
    user = User.objects.get(pk=user.pk)
    assert user.has_perm("party.view_party")
    assert user.has_perm("party.view_contactpoint")
    assert not user.has_perm("party.change_party")
    assert not user.has_perm("party.add_contactpoint")


@pytest.mark.django_db
@override_settings(SP_PARTY_SYNC=True, SP_PARTY_ADMIN_THIN=True)
def test_thin_admin_visible_to_staff_without_crm_groups():
    """Thin AUTH changelist stays usable for staff; CRM groups are not required."""
    from django.contrib.admin.sites import AdminSite
    from django.contrib.auth import get_user_model

    from socialprofile.admin import CustomUserAdmin
    from socialprofile.models import SocialProfile

    User = get_user_model()
    staff = User.objects.create_user(
        username="thinstaff",
        email="thinstaff@example.com",
        password="x",
        is_staff=True,
    )
    admin = CustomUserAdmin(SocialProfile, AdminSite())
    display = admin.get_list_display(request=None)
    assert display == CustomUserAdmin.THIN_LIST_DISPLAY
    assert "gender" not in display
    assert staff.is_staff
    # Staff without CRM groups still may change SocialProfile via model perms
    # when assigned; CRM Contatti mutate stays on party groups only.
    assert not Permission.objects.filter(
        group__user=staff, content_type__app_label="party"
    ).exists()

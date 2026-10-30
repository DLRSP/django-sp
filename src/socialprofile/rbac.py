"""AUTH-plane feature-group seeds (Django Group). Independent of party."""

from __future__ import annotations

import logging

from django.apps import apps
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)

AUTH_FEATURE_GROUPS = {
    "dlrsp:auth.user_manage": [
        ("socialprofile", "change_socialprofile"),
        ("socialprofile", "view_socialprofile"),
        ("socialprofile", "add_socialprofile"),
    ],
    "dlrsp:auth.oauth_monitor": [
        ("social_django", "view_usersocialauth"),
    ],
    "dlrsp:auth.session_monitor": [
        ("user_sessions", "view_session"),
        ("axes", "view_accessattempt"),
        ("axes", "view_accesslog"),
    ],
}


def seed_auth_feature_groups(**kwargs) -> None:
    try:
        Group = apps.get_model("auth", "Group")
        Permission = apps.get_model("auth", "Permission")
    except LookupError:
        return
    for group_name, perm_specs in AUTH_FEATURE_GROUPS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perms = []
        for app_label, codename in perm_specs:
            perm = Permission.objects.filter(
                content_type__app_label=app_label, codename=codename
            ).first()
            if perm is not None:
                perms.append(perm)
        if perms:
            group.permissions.set(perms)


def connect_rbac_signals() -> None:
    post_migrate.connect(
        seed_auth_feature_groups,
        sender=apps.get_app_config("socialprofile"),
        dispatch_uid="socialprofile.seed_auth_feature_groups",
    )

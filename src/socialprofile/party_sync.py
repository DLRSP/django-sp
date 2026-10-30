"""Optional Party dual-write from SocialProfile (django-party extra).

Gated by ``SP_PARTY_SYNC`` (default False). Never import party at module top.
Never invent ConsentRecord. Never write beddy/fiscal ExtIds. Failures are logged
and swallowed so login still commits.
"""

from __future__ import annotations

import logging
from typing import Any

from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)

EXTID_NAMESPACE = "socialprofile"

# Reserved for the SocialProfile→Party primary link (scheme=user, value=pk).
# Never accept IdP provider names that normalize into these schemes.
_RESERVED_EXTID_SCHEMES = frozenset({"user"})

# Provider schemes written as ExtId after normalizing ``*-oauth2`` suffixes.
_PROVIDER_EXTID_SCHEMES = frozenset(
    {
        "google",
        "facebook",
        "twitter",
        "instagram",
        "live",
        "linkedin",
        "discord",
        "github",
        "microsoft",
        "microsoft-graph",
        "apple",
        "gitlab",
        "bitbucket",
        "yahoo",
        "amazon",
        "vk",
        "odnoklassniki",
        "openid",
    }
)


def party_sync_enabled() -> bool:
    return bool(
        getattr(settings, "SP_PARTY_SYNC", False)
    ) and apps.is_installed("party")


def sync_party_from_profile(
    strategy, details, user=None, *args, **kwargs
) -> dict[str, Any] | None:
    """PSA pipeline step — append only when SP_PARTY_SYNC is on."""
    if user is None or not party_sync_enabled():
        return None
    try:
        _sync_user(user)
    except Exception:
        logger.exception(
            "party sync failed for user pk=%s; login continues",
            getattr(user, "pk", None),
        )
    return None


def sync_party_after_profile_save(user) -> None:
    """Dual-write Party after SocialProfileForm.save when SP_PARTY_SYNC is on.

    Fail-open: exceptions are logged; the profile row is already saved.
    Prefer the form/view hook over a global SocialProfile post_save so login
    pipeline, admin bulk edits, and unrelated saves do not storm Party writes.
    """
    if user is None or not party_sync_enabled():
        return
    try:
        _sync_user(user)
    except Exception:
        logger.exception(
            "party sync after profile save failed for user pk=%s",
            getattr(user, "pk", None),
        )


def _sync_user(user) -> None:
    from django.db import transaction
    from django.utils import timezone as dj_timezone
    from party.services import upsert_external_identity

    with transaction.atomic():
        now = dj_timezone.now()
        party = _ensure_party_for_user(user, now)
        # Idempotent when _ensure_party_for_user already created the link.
        upsert_external_identity(
            party,
            namespace=EXTID_NAMESPACE,
            scheme="user",
            value=str(user.pk),
            trust=80,
        )
        _sync_provider_uids(user, party)
        _sync_contact_fields(user, party, now)
        _sync_facts(user, party, now)


def _get_open_user_extid(user_pk: str):
    """Return the open socialprofile/user ExtId for this pk, or None."""
    from party.models import ExternalIdentity

    return (
        ExternalIdentity.objects.filter(
            namespace=EXTID_NAMESPACE,
            scheme="user",
            value=str(user_pk),
            valid_to__isnull=True,
        )
        .select_related("party")
        .first()
    )


def _ensure_party_for_user(user, now):
    """Resolve or create Party with a primary user ExtId in the same atomic unit.

    Prefer ExtId lookup first. When missing, create Party and the open
    socialprofile/user ExtId inside one savepoint so a concurrent winner's
    unique violation rolls back both rows (no orphan Party). On IntegrityError,
    re-fetch the ExtId that won and use that Party.
    """
    from django.db import IntegrityError, transaction
    from party.models import ExternalIdentity, Party

    user_pk = str(user.pk)
    ext = _get_open_user_extid(user_pk)
    if ext is not None:
        party = ext.party
    else:
        try:
            with transaction.atomic():
                party = Party.objects.create(
                    kind=Party.Kind.PERSON,
                    given_name=(getattr(user, "first_name", None) or "")[:128],
                    family_name=(getattr(user, "last_name", None) or "")[:128],
                    birth_date=getattr(user, "date_of_birth", None),
                )
                ExternalIdentity.objects.create(
                    party=party,
                    namespace=EXTID_NAMESPACE,
                    scheme="user",
                    value=user_pk,
                    trust=80,
                    valid_from=now,
                )
        except IntegrityError:
            ext = _get_open_user_extid(user_pk)
            if ext is None:
                raise
            party = ext.party

    edited = bool(getattr(user, "edited_by_user", False))
    if not edited:
        changed = False
        gn = (getattr(user, "first_name", None) or "").strip()
        fn = (getattr(user, "last_name", None) or "").strip()
        if gn and party.given_name != gn:
            party.given_name = gn[:128]
            changed = True
        if fn and party.family_name != fn:
            party.family_name = fn[:128]
            changed = True
        dob = getattr(user, "date_of_birth", None)
        if dob and party.birth_date != dob:
            party.birth_date = dob
            changed = True
        if changed:
            party.save()
    return party


def _provider_extid_scheme(provider: str) -> str | None:
    """Map PSA provider name → ExtId scheme, or None if reserved/unknown."""
    raw = (provider or "").strip().lower()
    if not raw:
        return None
    scheme = raw.replace("-oauth2", "").replace("_oauth2", "")
    if not scheme or scheme in _RESERVED_EXTID_SCHEMES:
        return None
    if scheme not in _PROVIDER_EXTID_SCHEMES:
        return None
    return scheme[:64]


def _sync_provider_uids(user, party) -> None:
    from party.services import upsert_external_identity

    try:
        from social_django.models import UserSocialAuth
    except ImportError:
        return
    for usa in UserSocialAuth.objects.filter(user=user):
        uid = (usa.uid or "").strip()
        if not uid:
            continue
        scheme = _provider_extid_scheme(usa.provider or "")
        if scheme is None:
            logger.info(
                "skip ExtId for provider=%r user=%s (reserved or unknown)",
                usa.provider,
                user.pk,
            )
            continue
        try:
            upsert_external_identity(
                party,
                namespace=EXTID_NAMESPACE,
                scheme=scheme,
                value=uid[:255],
                trust=70,
            )
        except ValueError:
            logger.warning(
                "ExtId %s/%s already bound; skip for user %s",
                EXTID_NAMESPACE,
                scheme,
                user.pk,
            )


def _sync_contact_fields(user, party, now) -> None:
    from party.services import upsert_contact_point, upsert_postal_address

    phone = (getattr(user, "phone_number", None) or "").strip()
    if phone:
        upsert_contact_point(
            party,
            channel="phone",
            value=phone,
            use="other",
            valid_from=now,
        )
    # Login email stays on SocialProfile; optional email ContactPoint
    # (use=other) only when SP_PARTY_MIRROR_LOGIN_EMAIL is enabled.
    email = (getattr(user, "email", None) or "").strip()
    if email and getattr(settings, "SP_PARTY_MIRROR_LOGIN_EMAIL", False):
        upsert_contact_point(
            party,
            channel="email",
            value=email,
            use="other",
            valid_from=now,
        )
    line1 = (getattr(user, "address", None) or "").strip()
    city = (getattr(user, "city", None) or "").strip()
    postal = (getattr(user, "postalcode", None) or "").strip()
    country = getattr(user, "country", None)
    country_code = ""
    if country is not None:
        country_code = str(getattr(country, "code", country) or "")[:2]
    if any((line1, city, postal, country_code)):
        upsert_postal_address(
            party,
            line1=line1,
            city=city,
            postal_code=postal,
            country=country_code,
            valid_from=now,
        )


def _sync_facts(user, party, now) -> None:
    from party.services import upsert_party_fact

    def fact(key: str, value, source: str = "socialprofile") -> None:
        if value is None or value == "":
            return
        upsert_party_fact(
            party, key=key, value=str(value), source=source, valid_from=now
        )

    fact("gender", getattr(user, "gender", None))
    fact("bio", getattr(user, "description", None))
    fact("homepage", getattr(user, "url", None))
    fact("company", getattr(user, "company", None))

    for provider in ("google", "facebook", "twitter", "instagram", "live"):
        email = getattr(user, f"{provider}_email", None)
        # Provider emails → Fact only (never ContactPoint).
        fact(f"idp.{provider}.email", email, source=provider)
        fact(
            f"idp.{provider}.username",
            getattr(user, f"{provider}_username", None),
            source=provider,
        )
        fact(
            f"idp.{provider}.profile_url",
            getattr(user, f"{provider}_url", None),
            source=provider,
        )
        fact(
            f"idp.{provider}.language",
            getattr(user, f"{provider}_language", None),
            source=provider,
        )
        fact(
            f"idp.{provider}.verified",
            getattr(user, f"{provider}_verified", None),
            source=provider,
        )

    # Obsolete Google+ metrics → closed facts.
    for key, attr in (
        ("idp.google.is_plus_user", "google_isPlusUser"),
        ("idp.google.circled_by_count", "google_circledByCount"),
    ):
        val = getattr(user, attr, None)
        if val is None or val == "" or val is False or val == 0:
            continue
        upsert_party_fact(
            party,
            key=key,
            value=str(val),
            source="google",
            valid_from=now,
            valid_to=now,
        )

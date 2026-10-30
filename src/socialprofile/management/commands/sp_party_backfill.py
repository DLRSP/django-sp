"""Backfill Party ExtIds from SocialProfile / UserSocialAuth (opt-in party extra)."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Run SocialProfile→Party dual-write for each user (ExtId user + providers, "
        "anagrafica, facts). Requires party installed and SP_PARTY_SYNC (or --force). "
        "Does not invent ConsentRecord. Safe to re-run."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Count users without writing.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Max users to process (0 = all).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run even when SP_PARTY_SYNC is False.",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        limit = options["limit"]
        force = options["force"]
        try:
            from django.apps import apps

            if not apps.is_installed("party"):
                self.stderr.write("party is not installed; abort.")
                return
            from socialprofile.party_sync import _sync_user, party_sync_enabled
        except ImportError as exc:
            self.stderr.write(f"party sync unavailable: {exc}")
            return

        if not force and not party_sync_enabled():
            self.stderr.write(
                "SP_PARTY_SYNC is off; pass --force to backfill without enabling sync."
            )
            return

        User = get_user_model()
        qs = User.objects.order_by("pk")
        if limit:
            qs = qs[:limit]
        total = qs.count() if hasattr(qs, "count") else 0
        if dry:
            self.stdout.write(self.style.SUCCESS(f"dry_run users={total}"))
            return
        done = 0
        for user in qs.iterator():
            with transaction.atomic():
                _sync_user(user)
            done += 1
        self.stdout.write(self.style.SUCCESS(f"backfill synced users={done}"))

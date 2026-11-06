# Generated manually for email password / OTP / trusted device

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("socialprofile", "0029_socialprofiles_emails"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialprofile",
            name="email_verified_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Set when email ownership is proven (email OTP).",
                null=True,
                verbose_name="Email verified at",
            ),
        ),
        migrations.CreateModel(
            name="EmailLoginChallenge",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(db_index=True, max_length=254)),
                (
                    "purpose",
                    models.CharField(
                        choices=[
                            ("login_otp", "Login OTP"),
                            ("register_verify", "Register verify"),
                            ("password_reset", "Password reset"),
                        ],
                        max_length=32,
                    ),
                ),
                ("code_hash", models.CharField(max_length=64)),
                ("salt", models.CharField(max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("attempt_count", models.PositiveSmallIntegerField(default=0)),
                (
                    "request_ip",
                    models.CharField(blank=True, default="", max_length=64),
                ),
            ],
            options={
                "verbose_name": "Email login challenge",
                "verbose_name_plural": "Email login challenges",
            },
        ),
        migrations.CreateModel(
            name="TrustedDevice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "selector",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("token_hash", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user_agent",
                    models.CharField(blank=True, default="", max_length=256),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trusted_devices",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Trusted device",
                "verbose_name_plural": "Trusted devices",
            },
        ),
        migrations.AddIndex(
            model_name="emailloginchallenge",
            index=models.Index(
                fields=["email", "purpose", "consumed_at"],
                name="socialprofi_email_p_idx",
            ),
        ),
    ]

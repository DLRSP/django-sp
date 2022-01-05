import django.contrib.auth.models
import django.core.validators
import image_cropping.fields
from django.db import migrations, models

import socialprofile.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0011_update_proxy_permissions"),
    ]

    operations = [
        migrations.CreateModel(
            name="SocialProfile",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            b"unique": "A user with that username already exists."
                        },
                        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=30,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                b"^[\\w.@+-]+$",
                                "Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.",
                            )
                        ],
                        verbose_name="Username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="First Name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="Last Name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="Email Address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_of_birth",
                    models.DateField(null=True, verbose_name="Date of Birth"),
                ),
                (
                    "date_joined",
                    models.DateTimeField(auto_now_add=True, verbose_name="Date Joined"),
                ),
                (
                    "date_modified",
                    models.DateTimeField(auto_now=True, verbose_name="Date Updated"),
                ),
                (
                    "country",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Country"
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("male", "Male"),
                            ("female", "Female"),
                            ("other", "Other"),
                            (b"", b""),
                        ],
                        max_length=10,
                        verbose_name="Gender",
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        blank=True,
                        help_text="Where can we find out more about you?",
                        max_length=500,
                        verbose_name="Homepage",
                    ),
                ),
                (
                    "image_url",
                    models.URLField(
                        blank=True, max_length=500, verbose_name="Avatar Picture"
                    ),
                ),
                (
                    "image",
                    image_cropping.fields.ImageCropField(
                        blank=True, upload_to=b"user/"
                    ),
                ),
                (
                    "cropping",
                    image_cropping.fields.ImageRatioField(
                        "image",
                        "120x100",
                        adapt_rotation=False,
                        allow_fullsize=True,
                        free_crop=False,
                        help_text=None,
                        hide_image_field=False,
                        size_warning=False,
                        verbose_name="cropping",
                    ),
                ),
                (
                    "cropping_free",
                    image_cropping.fields.ImageRatioField(
                        "image",
                        "300x300",
                        adapt_rotation=False,
                        allow_fullsize=False,
                        free_crop=True,
                        help_text=None,
                        hide_image_field=False,
                        size_warning=True,
                        verbose_name="cropping free",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Tell us about yourself!",
                        verbose_name="Description",
                    ),
                ),
                (
                    "manually_edited",
                    models.BooleanField(default=False, verbose_name="Manually Edited"),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=16,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                                regex=b"^\\+\\d{8,15}$",
                            )
                        ],
                    ),
                ),
                (
                    "sort",
                    socialprofile.models.IntegerRangeField(
                        blank=True, default=1, verbose_name="Sort Order"
                    ),
                ),
                (
                    "visible",
                    models.BooleanField(
                        default=False, verbose_name="Visible in the Public Pages"
                    ),
                ),
                (
                    "title",
                    models.CharField(blank=True, max_length=500, verbose_name="Title"),
                ),
                (
                    "role",
                    models.CharField(blank=True, max_length=500, verbose_name="Role"),
                ),
                ("function_01", models.CharField(blank=True, max_length=200)),
                ("function_02", models.CharField(blank=True, max_length=200)),
                ("function_03", models.CharField(blank=True, max_length=200)),
                ("function_04", models.CharField(blank=True, max_length=200)),
                ("function_05", models.CharField(blank=True, max_length=200)),
                ("function_06", models.CharField(blank=True, max_length=200)),
                ("function_07", models.CharField(blank=True, max_length=200)),
                ("function_08", models.CharField(blank=True, max_length=200)),
                ("function_09", models.CharField(blank=True, max_length=200)),
                ("function_10", models.CharField(blank=True, max_length=200)),
                (
                    "editByGoogle",
                    models.BooleanField(
                        default=False, verbose_name="Google Edit User's Info"
                    ),
                ),
                (
                    "google_isPlusUser",
                    models.BooleanField(default=False, verbose_name="Google Plus"),
                ),
                (
                    "google_plusUrl",
                    models.URLField(
                        blank=True, max_length=500, verbose_name="Google Plus Page"
                    ),
                ),
                (
                    "google_circledByCount",
                    models.IntegerField(
                        blank=True, default=0, verbose_name="Google Circle byCount"
                    ),
                ),
                (
                    "google_language",
                    models.CharField(
                        blank=True, max_length=2, verbose_name="Google Language"
                    ),
                ),
                (
                    "google_kind",
                    models.CharField(
                        blank=True, max_length=2, verbose_name="Google Kind"
                    ),
                ),
                (
                    "google_verified",
                    models.BooleanField(default=False, verbose_name="Google Verified"),
                ),
            ],
            options={
                "ordering": ["username"],
                "abstract": False,
                "verbose_name_plural": "Social Profiles",
                "proxy": False,
                "verbose_name": "Social Profile",
                "swappable": "AUTH_USER_MODEL",
            },
            managers=[
                ("objects", socialprofile.models.SocialProfileManager()),
            ],
        ),
        migrations.CreateModel(
            name="Group",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
            },
            bases=("auth.group",),
            managers=[
                ("objects", django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Permission",
                verbose_name="user permissions",
            ),
        ),
    ]

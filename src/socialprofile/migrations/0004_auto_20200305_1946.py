# Generated by Django 2.2.11 on 2020-03-05 18:46

import django.core.validators
import image_cropping.fields
from django.db import migrations, models

import socialprofile.models


class Migration(migrations.Migration):

    dependencies = [
        ("socialprofile", "0003_merge_20200207_1147"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialprofile",
            name="address",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Address"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="city",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="City"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="company",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Company"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="last_accessed",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="postalcode",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Postal Code"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="country",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Country"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True, verbose_name="Date of Birth"),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Tell us about yourself!",
                null=True,
                verbose_name="Description",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="editByGoogle",
            field=models.NullBooleanField(
                default=False, verbose_name="Google Edit User's Info"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="email",
            field=models.EmailField(max_length=254, verbose_name="Email Address"),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_01",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_02",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_03",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_04",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_05",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_06",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_07",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_08",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_09",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="function_10",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("other", "Other"),
                    ("", ""),
                ],
                max_length=10,
                null=True,
                verbose_name="Gender",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="google_circledByCount",
            field=models.IntegerField(
                blank=True, default=0, null=True, verbose_name="Google Circle byCount"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="google_isPlusUser",
            field=models.NullBooleanField(default=False, verbose_name="Google Plus"),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="google_kind",
            field=models.CharField(
                blank=True, max_length=2, null=True, verbose_name="Google Kind"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="google_language",
            field=models.CharField(
                blank=True, max_length=2, null=True, verbose_name="Google Language"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="google_plusUrl",
            field=models.URLField(
                blank=True, max_length=500, null=True, verbose_name="Google Plus Page"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="google_verified",
            field=models.NullBooleanField(
                default=False, verbose_name="Google Verified"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="image",
            field=image_cropping.fields.ImageCropField(
                blank=True, null=True, upload_to="user/"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="image_url",
            field=models.URLField(
                blank=True, max_length=500, null=True, verbose_name="Avatar Picture"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="is_active",
            field=models.NullBooleanField(
                default=True,
                help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                verbose_name="active",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="is_staff",
            field=models.NullBooleanField(
                default=False,
                help_text="Designates whether the user can log into this admin site.",
                verbose_name="staff status",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="manually_edited",
            field=models.NullBooleanField(
                default=False, verbose_name="Manually Edited"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=16,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                        regex="^\\+\\d{8,15}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="role",
            field=models.CharField(
                blank=True, max_length=500, null=True, verbose_name="Role"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="sort",
            field=socialprofile.models.IntegerRangeField(
                blank=True, default=1, null=True, verbose_name="Sort Order"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="title",
            field=models.CharField(
                blank=True,
                default="Member",
                max_length=500,
                null=True,
                verbose_name="Title",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="url",
            field=models.URLField(
                blank=True,
                help_text="Where can we find out more about you?",
                max_length=500,
                null=True,
                verbose_name="Homepage",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="username",
            field=models.CharField(
                error_messages={"unique": "A user with that username already exists."},
                help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
                max_length=30,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[\\w.@+-]+$",
                        "Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.",
                    )
                ],
                verbose_name="Username",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="visible",
            field=models.NullBooleanField(
                default=False,
                help_text="Designates whether this user should be visible by all. Unselect this make your account private!",
                verbose_name="Visible in the Public Pages",
            ),
        ),
    ]
# Generated by Django 3.2.11 on 2022-01-10 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("socialprofile", "0023_auto_20211216_1745"),
    ]

    operations = [
        migrations.AlterField(
            model_name="socialprofile",
            name="edited_by_facebook",
            field=models.BooleanField(
                blank=True, default=False, verbose_name="Facebook edited"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="edited_by_google",
            field=models.BooleanField(
                blank=True, default=False, verbose_name="Google edited"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="edited_by_instagram",
            field=models.BooleanField(
                blank=True, default=False, verbose_name="Instagram edited"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="edited_by_twitter",
            field=models.BooleanField(
                blank=True, default=False, verbose_name="Twitter edited"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="edited_by_user",
            field=models.BooleanField(default=False, verbose_name="User edited"),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="google_isPlusUser",
            field=models.BooleanField(
                blank=True, default=False, null=True, verbose_name="Google Plus"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="google_verified",
            field=models.BooleanField(
                blank=True, default=False, null=True, verbose_name="Google Verified"
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="image_avatar",
            field=models.CharField(
                blank=True,
                choices=[
                    ("socials", "Socials"),
                    ("predef", "Predefined"),
                    ("custom", "Custom"),
                ],
                default="socials",
                max_length=100,
                verbose_name="Avatar Picture",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="image_avatar_predef",
            field=models.CharField(
                blank=True,
                choices=[
                    ("avatar1.png", "Male 1"),
                    ("avatar2.png", "Male 2"),
                    ("avatar3.png", "Female 1"),
                    ("avatar4.png", "Male 3"),
                    ("avatar5.png", "Male 4"),
                    ("avatar6.png", "Male 5"),
                    ("avatar7.png", "Male 6"),
                    ("avatar8.png", "Female 2"),
                ],
                default="avatar1.png",
                max_length=100,
                verbose_name="Predef Avatar Picture",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="is_active",
            field=models.BooleanField(
                blank=True,
                default=True,
                help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                null=True,
                verbose_name="Active",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="is_staff",
            field=models.BooleanField(
                blank=True,
                default=False,
                help_text="Designates whether the user can log into this admin site.",
                null=True,
                verbose_name="Staff",
            ),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="twitter_verified",
            field=models.BooleanField(
                blank=True, default=False, null=True, verbose_name="Twitter Verified"
            ),
        ),
    ]

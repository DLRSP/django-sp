# Generated by Django 2.2.24 on 2021-11-29 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("socialprofile", "0016_auto_20211129_2259"),
    ]

    operations = [
        migrations.RenameField(
            model_name="socialprofile",
            old_name="username_facebook",
            new_name="facebook_username",
        ),
        migrations.RenameField(
            model_name="socialprofile",
            old_name="username_instagram",
            new_name="instagram_username",
        ),
    ]

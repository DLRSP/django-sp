# Generated by Django 2.2.24 on 2021-11-29 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("socialprofile", "0015_auto_20211129_2117"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialprofile",
            name="google_username",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="Google Username"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="instagram_url",
            field=models.URLField(
                blank=True, max_length=500, null=True, verbose_name="Instagram Profile"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="twitter_username",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="Twitter Username"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="username_facebook",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="Facebook Username"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="username_instagram",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="Instagram Username"
            ),
        ),
    ]
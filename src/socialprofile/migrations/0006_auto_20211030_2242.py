# Generated by Django 2.2.19 on 2021-10-30 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("socialprofile", "0005_auto_20211030_2237"),
    ]

    operations = [
        migrations.AlterField(
            model_name="socialprofile",
            name="google_language",
            field=models.CharField(
                blank=True, max_length=10, null=True, verbose_name="Google Language"
            ),
        ),
    ]
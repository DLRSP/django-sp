# Generated by Django 4.2.4 on 2023-08-05 15:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("socialprofile", "0027_delete_proxy_phonedevice"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="proxysession",
            options={
                "verbose_name": "Monitor: session",
                "verbose_name_plural": "Monitor: sessions",
            },
        ),
    ]

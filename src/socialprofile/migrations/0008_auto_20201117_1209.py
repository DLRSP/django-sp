# Generated by Django 2.2.16 on 2020-11-17 11:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("socialprofile", "0007_auto_20200403_1525"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="proxysession",
            options={
                "verbose_name": "Monitor: sessione",
                "verbose_name_plural": "Monitor: sessioni",
            },
        ),
    ]

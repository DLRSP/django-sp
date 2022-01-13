# Generated by Django 2.2.25 on 2021-12-16 16:45

import image_cropping.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("socialprofile", "0022_auto_20211215_2357"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="socialprofile",
            name="edited_by_provider",
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="edited_by_facebook",
            field=models.NullBooleanField(
                default=False, verbose_name="Facebook edited"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="edited_by_google",
            field=models.NullBooleanField(default=False, verbose_name="Google edited"),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="edited_by_instagram",
            field=models.NullBooleanField(
                default=False, verbose_name="Instagram edited"
            ),
        ),
        migrations.AddField(
            model_name="socialprofile",
            name="edited_by_twitter",
            field=models.NullBooleanField(default=False, verbose_name="Twitter edited"),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="cropping",
            field=image_cropping.fields.ImageRatioField(
                "image",
                "120x100",
                adapt_rotation=False,
                allow_fullsize=False,
                free_crop=False,
                help_text=None,
                hide_image_field=False,
                size_warning=True,
                verbose_name="cropping",
            ),
        ),
    ]
import image_cropping.fields
from django.db import migrations

import socialprofile.models


class Migration(migrations.Migration):

    dependencies = [
        ("socialprofile", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="socialprofile",
            name="image",
            field=image_cropping.fields.ImageCropField(upload_to="user/", blank=True),
        ),
        migrations.AlterField(
            model_name="socialprofile",
            name="sort",
            field=socialprofile.models.IntegerRangeField(
                default=1, verbose_name="Sort Order", blank=True
            ),
        ),
    ]

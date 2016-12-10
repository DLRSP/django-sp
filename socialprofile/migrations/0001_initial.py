# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import image_cropping.fields
import django.core.validators
import socialprofile.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('gender', models.CharField(blank=True, max_length=10, verbose_name='Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('', '')])),
                ('url', models.URLField(help_text='Where can we find out more about you?', max_length=500, verbose_name='Homepage', blank=True)),
                ('image_url', models.URLField(max_length=500, verbose_name='Avatar Picture', blank=True)),
                ('image', image_cropping.fields.ImageCropField(upload_to='staff/', blank=True)),
                (b'cropping', image_cropping.fields.ImageRatioField('image', '120x100', hide_image_field=False, size_warning=False, allow_fullsize=True, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping')),
                (b'cropping_free', image_cropping.fields.ImageRatioField('image', '300x300', hide_image_field=False, size_warning=True, allow_fullsize=False, free_crop=True, adapt_rotation=False, help_text=None, verbose_name='cropping free')),
                ('description', models.TextField(help_text='Tell us about yourself!', verbose_name='Description', blank=True)),
                ('manually_edited', models.BooleanField(default=False, verbose_name='Manually Edited')),
                ('sort', socialprofile.models.IntegerRangeField(default=1, verbose_name='Order', blank=True)),
                ('visible', models.BooleanField(default=False, verbose_name='Visible in the Public Pages')),
                ('title', models.CharField(max_length=500, blank=True)),
                ('role', models.CharField(max_length=500, blank=True)),
                ('function_01', models.CharField(max_length=200, blank=True)),
                ('function_02', models.CharField(max_length=200, blank=True)),
                ('function_03', models.CharField(max_length=200, blank=True)),
                ('function_04', models.CharField(max_length=200, blank=True)),
                ('function_05', models.CharField(max_length=200, blank=True)),
                ('function_06', models.CharField(max_length=200, blank=True)),
                ('function_07', models.CharField(max_length=200, blank=True)),
                ('function_08', models.CharField(max_length=200, blank=True)),
                ('function_09', models.CharField(max_length=200, blank=True)),
                ('function_10', models.CharField(max_length=200, blank=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['username'],
                'verbose_name': 'Social Profile',
                'verbose_name_plural': 'Social Profiles',
            },
            managers=[
                ('objects', socialprofile.models.UserManager()),
            ],
        ),
    ]

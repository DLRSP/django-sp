# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Alternative implementation of Django's authentication User model, which allows to authenticate against the OAuth.
This alternative implementation is activated by setting ``AUTH_USER_MODEL = 'socialprofile.SocialProfile'`` in
settings.py, otherwise the default Django or another implementation is used.
"""
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from image_cropping.fields import ImageRatioField, ImageCropField

import logging
LOGGER = logging.getLogger(name='socialprofile.models')

class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)
	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value':self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)

class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(is_active=True, **{self.model.USERNAME_FIELD: username})

@python_2_unicode_compatible
class SocialProfile(AbstractUser):
    """
    Alternative implementation of Django's User model allowing to authenticate against the OAuth.
    """
    objects = UserManager()

    GENDER_CHOICES = (
        (_('male'), _('Male')),
        (_('female'), _('Female')),
        (_('other'), _('Other')),
        ('', '')
    )
    gender = models.CharField(max_length=10, blank=True, choices=GENDER_CHOICES, verbose_name=_("Gender"))
    url = models.URLField(blank=True, verbose_name=_("Homepage"), help_text=_("Where can we find out more about you?"), max_length=500)
    image_url = models.URLField(blank=True, verbose_name=_("Avatar Picture"), max_length=500)
    image = ImageCropField(upload_to='user/',blank=True)
    cropping = ImageRatioField('image', '120x100', allow_fullsize=True)
    cropping_free = ImageRatioField('image', '300x300', free_crop=True, size_warning=True)
    description = models.TextField(blank=True, verbose_name=_("Description"), help_text=_("Tell us about yourself!"))
    manually_edited = models.BooleanField(default=False, verbose_name=_("Manually Edited"))
	
	# Add for Staff Infos
    sort = IntegerRangeField(default=1, min_value=1, max_value=100,blank=True, verbose_name=_("Sort Order"))
    visible = models.BooleanField(default=False, blank=True, verbose_name=_("Visible in the Public Pages"))
    title = models.CharField(max_length=500,blank=True)
    role = models.CharField(max_length=500,blank=True)
    function_01 = models.CharField(max_length=200,blank=True)
    function_02 = models.CharField(max_length=200,blank=True)
    function_03 = models.CharField(max_length=200,blank=True)
    function_04 = models.CharField(max_length=200,blank=True)
    function_05 = models.CharField(max_length=200,blank=True)
    function_06 = models.CharField(max_length=200,blank=True)
    function_07 = models.CharField(max_length=200,blank=True)
    function_08 = models.CharField(max_length=200,blank=True)
    function_09 = models.CharField(max_length=200,blank=True)
    function_10 = models.CharField(max_length=200,blank=True)

    class Meta(object):
        verbose_name = _("Social Profile")
        verbose_name_plural = _("Social Profiles")
        ordering = ['username']

    @models.permalink
    def get_absolute_url(self):
        return 'sp_profile_other_view_page', [self.username]

    def get_username(self):
        if self.is_staff:
            return self.username
        return self.email or '<anonymous>'

    def __str__(self):
        return self.get_username()

    def get_full_name(self):
        full_name = super(SocialProfile, self).get_full_name()
        if full_name:
            return full_name
        return self.get_short_name()

    def get_short_name(self):
        short_name = super(SocialProfile, self).get_short_name()
        if short_name:
            return short_name
        return self.email

    # def validate_unique(self, exclude=self.id):
        # """
        # Since the email address is used as the primary identifier, we must ensure that it is
        # unique. However, this can not be done on the field declaration since is only applies to
        # active users. Inactive users can not login anyway, so we don't need a unique constraint
        # for them.
        # """
        # super(SocialProfile, self).validate_unique(exclude)
        # if self.email and get_user_model().objects.exclude(id=self.id).filter(is_active=True, email__exact=self.email).exists():
            # msg = _("A customer with the e-mail address ‘{email}’ already exists.")
            # raise ValidationError({'email': msg.format(email=self.email)})

		
		
		
# class UserDetails(models.Model):
    # type = models.OneToOneField('SocialProfile')
    # extra_info = models.CharField(max_length=600)
	
# def create_user_profile(sender, instance, created, **kwargs):
    # """Creates a UserProfile Object Whenever a User Object is Created"""
    # if created:
        # SocialProfile.objects.create(user=instance)


# post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)

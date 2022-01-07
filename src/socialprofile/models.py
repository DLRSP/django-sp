# -*- coding: utf-8 -*-
"""
Alternative implementation of Django's authentication User model, which allows to authenticate against the OAuth.
This alternative implementation is activated by setting ``AUTH_USER_MODEL = 'socialprofile.SocialProfile'`` in
settings.py, otherwise the default Django or another implementation is used.
"""
import logging
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from image_cropping.fields import ImageCropField, ImageRatioField
from django_countries.fields import CountryField
# Older Django <3.0 (also deprecated in 2.0):
# from django.contrib.staticfiles.templatetags.staticfiles import static
# Django 3.0+
from django.templatetags.static import static

LOGGER = logging.getLogger(name="socialprofile.models")


class IntegerRangeField(models.IntegerField):
    def __init__(
        self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs
    ):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"min_value": self.min_value, "max_value": self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class SocialProfileManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, username):
        try:
            return self.get(username=username)
        except self.model.DoesNotExist:
            return self.get(is_active=True, email=username)

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        :param str email: user email
        :param str password: user password
        :param bool is_staff: whether user staff or not
        :param bool is_superuser: whether user admin or not
        :return socialprofile.models.SocialProfile user: user
        :raise ValueError: email is not set
        """
        now = timezone.localtime(timezone.now())
        if not email:
            raise ValueError(_("The given email must be set"))
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a SocialProfile with the given email and password.
        :param str email: user email
        :param str password: user password
        :return socialprofile.models.SocialProfile user: regular user
        """
        is_staff = extra_fields.pop("is_staff", False)
        is_superuser = extra_fields.pop("is_superuser", False)
        return self._create_user(
            email, password, is_staff, is_superuser, **extra_fields
        )

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class AbstractSocialProfile(AbstractBaseUser, PermissionsMixin):
    """
    Alternative implementation of Django's User model allowing to authenticate against the OAuth.

    Inherits from both the AbstractBaseUser and PermissionMixin.
    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser
    """

    username_validator = ASCIIUsernameValidator()

    GENDER_CHOICES = (
        ("male", _("Male")),
        ("female", _("Female")),
        ("unknown", _("Unknown")),
    )

    AVATAR_CHOICES = (
        ("socials", _("Socials")),
        ("predef", _("Predefined")),
        ("custom", _("Custom")),
    )

    AVATAR_IMG_CHOICES = (
        ("avatar1.png", _("Male 1")),
        ("avatar2.png", _("Male 2")),
        ("avatar3.png", _("Female 1")),
        ("avatar4.png", _("Male 3")),
        ("avatar5.png", _("Male 4")),
        ("avatar6.png", _("Male 5")),
        ("avatar7.png", _("Male 6")),
        ("avatar8.png", _("Female 2")),
    )

    BOOLEAN_YN = (
        (True, _("Yes")),
        (False, _("No")),
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    username = models.CharField(
        _("Username"),
        max_length=30,
        unique=True,
        blank=False,
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only"
        ),
        validators=[
            RegexValidator(
                r"^[\w.@+-]+$",
                _(
                    "Enter a valid username. This value may contain "
                    "30 characters or fewer. Only letters, numbers "
                    "and @/./+/-/_ characters"
                ),
            ),
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(
        verbose_name=_("First Name"), max_length=30, blank=True
    )
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=30, blank=True)
    gender = models.CharField(
        verbose_name=_("Gender"),
        max_length=10,
        null=False,
        blank=None,
        default="unknown",
        choices=GENDER_CHOICES,
    )
    email = models.EmailField(
        verbose_name=_("Email Address"), max_length=254, null=False, blank=False
    )
    is_staff = models.NullBooleanField(
        verbose_name=_("Staff"),
        default=False,
        null=True,
        blank=True,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.NullBooleanField(
        verbose_name=_("Active"),
        default=True,
        null=True,
        blank=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this "
            "instead of deleting accounts."
        ),
    )
    date_of_birth = models.DateField(
        verbose_name=_("Date of Birth"), null=True, blank=True
    )
    date_joined = models.DateTimeField(verbose_name=_("Date Joined"), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_("Date Updated"), auto_now=True)

    # status = models.ForeignKey(MembershipStatus, on_delete=models.SET_NULL, null=True, default=1)
    country = CountryField(_("Country"), null=True, blank=True)

    city = models.CharField(
        verbose_name=_("City"), max_length=255, null=True, blank=True
    )
    address = models.CharField(
        verbose_name=_("Address"), max_length=255, null=True, blank=True
    )
    postalcode = models.CharField(
        verbose_name=_("Postal Code"), max_length=255, null=True, blank=True
    )

    url = models.URLField(
        verbose_name=_("Homepage"),
        help_text=_("Where can we find out more about you?"),
        max_length=500,
        null=True,
        blank=True,
    )
    image_url = models.URLField(
        verbose_name=_("Avatar Picture"), max_length=500, null=True, blank=True
    )

    image_avatar = models.CharField(
        verbose_name=_("Avatar Picture"),
        max_length=100,
        null=False,
        blank=True,
        default="socials",
        choices=AVATAR_CHOICES,
    )
    image_avatar_predef = models.CharField(
        verbose_name=_("Predef Avatar Picture"),
        max_length=100,
        null=False,
        blank=True,
        default="avatar1.png",
        choices=AVATAR_IMG_CHOICES,
    )
    # Add Images
    # image = models.ImageField(upload_to="user/", null=True, blank=True)
    image = ImageCropField(upload_to="user/", null=True, blank=True)
    cropping = ImageRatioField("image", "120x100", allow_fullsize=False, size_warning=True)
    cropping_free = ImageRatioField(
        "image", "300x300", free_crop=True, size_warning=True
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Tell us about yourself!"),
        null=True,
        blank=True,
    )

    # Add Contact info
    # max_length=15->'^\+?1?\d{9,15}$'
    phone_regex = RegexValidator(
        regex=r"^\+\d{8,15}$",
        message=_(
            "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        ),
    )
    phone_number = models.CharField(
        verbose_name=_("Phone Number"),
        validators=[phone_regex],
        max_length=16,
        null=True,
        blank=True,
    )

    # Add for Work Infos
    sort = IntegerRangeField(
        verbose_name=_("Sort order"),
        default=1,
        min_value=1,
        max_value=100000000,
        null=True,
        blank=True,
    )
    visible = models.BooleanField(
        verbose_name=_("Public"),
        default=True,
        null=False,
        blank=False,
        choices=BOOLEAN_YN,
        help_text=_(
            "Designates whether this user should be visible by all. Select 'no' this make "
            "your account private!"
        ),
    )

    company = models.CharField(
        verbose_name=_("Company"), max_length=255, null=True, blank=True
    )
    title = models.CharField(
        verbose_name=_("Title"),
        default=_("Member"),
        max_length=500,
        null=True,
        blank=True,
    )
    role = models.CharField(
        verbose_name=_("Role"), max_length=500, null=True, blank=True
    )
    function_01 = models.CharField(max_length=200, null=True, blank=True)
    function_02 = models.CharField(max_length=200, null=True, blank=True)
    function_03 = models.CharField(max_length=200, null=True, blank=True)
    function_04 = models.CharField(max_length=200, null=True, blank=True)
    function_05 = models.CharField(max_length=200, null=True, blank=True)
    function_06 = models.CharField(max_length=200, null=True, blank=True)
    function_07 = models.CharField(max_length=200, null=True, blank=True)
    function_08 = models.CharField(max_length=200, null=True, blank=True)
    function_09 = models.CharField(max_length=200, null=True, blank=True)
    function_10 = models.CharField(max_length=200, null=True, blank=True)

    edited_by_user = models.NullBooleanField(
        verbose_name=_("User edited"), default=False, null=False, blank=False
    )
    edited_by_google = models.NullBooleanField(
        verbose_name=_("Google edited"), default=False, null=False, blank=True
    )
    edited_by_twitter = models.NullBooleanField(
        verbose_name=_("Twitter edited"), default=False, null=False, blank=True
    )
    edited_by_facebook = models.NullBooleanField(
        verbose_name=_("Facebook edited"), default=False, null=False, blank=True
    )
    edited_by_instagram = models.NullBooleanField(
        verbose_name=_("Instagram edited"), default=False, null=False, blank=True
    )

    # Add Info retrieved by Google
    google_username = models.CharField(
        _("Google Username"),
        max_length=30,
        # unique=True,
        blank=True,
    )
    google_isPlusUser = models.NullBooleanField(
        verbose_name=_("Google Plus"), default=False, null=True, blank=True
    )
    google_url = models.URLField(
        verbose_name=_("Google Plus Page"), max_length=500, null=True, blank=True
    )
    google_circledByCount = models.IntegerField(
        verbose_name=_("Google Circle byCount"), default=0, null=True, blank=True
    )
    google_language = models.CharField(
        verbose_name=_("Google Language"), max_length=10, null=True, blank=True
    )
    google_kind = models.CharField(
        verbose_name=_("Google Kind"), max_length=15, null=True, blank=True
    )
    google_verified = models.NullBooleanField(
        verbose_name=_("Google Verified"), default=False, null=True, blank=True
    )
    google_avatar = models.URLField(
        verbose_name=_("Google Avatar"), max_length=500, null=True, blank=True
    )

    # Add Info retrieved by Twitter
    twitter_username = models.CharField(
        _("Twitter Username"),
        max_length=30,
        # unique=True,
        blank=True,
    )
    twitter_language = models.CharField(
        verbose_name=_("Twitter Language"), max_length=10, null=True, blank=True
    )
    twitter_verified = models.NullBooleanField(
        verbose_name=_("Twitter Verified"), default=False, null=True, blank=True
    )
    twitter_url = models.URLField(
        verbose_name=_("Twitter Profile"),
        max_length=500,
        null=True,
        blank=True,
    )
    twitter_avatar = models.URLField(
        verbose_name=_("Twitter Avatar"), max_length=500, null=True, blank=True
    )

    facebook_username = models.CharField(
        _("Facebook Username"),
        max_length=30,
        # unique=True,
        blank=True,
    )
    facebook_url = models.URLField(
        verbose_name=_("Facebook Profile"),
        max_length=500,
        null=True,
        blank=True,
    )
    facebook_avatar = models.URLField(
        verbose_name=_("Facebook Avatar"), max_length=500, null=True, blank=True
    )

    instagram_username = models.CharField(
        _("Instagram Username"),
        max_length=30,
        # unique=True,
        blank=True,
    )
    instagram_url = models.URLField(
        verbose_name=_("Instagram Profile"),
        max_length=500,
        null=True,
        blank=True,
    )
    instagram_avatar = models.URLField(
        verbose_name=_("Instagram Avatar"), max_length=500, null=True, blank=True
    )

    objects = SocialProfileManager()

    class Meta(object):
        verbose_name = _("Social Profile")
        verbose_name_plural = _("Social Profiles")
        ordering = ["username"]
        proxy = False
        abstract = True

    # def save(self, *args, **kwargs):
    # if not self.username:
    # self.username = self.get_email()
    # super(AbstractSocialProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.get_email()

    def get_absolute_url(self):
        return reverse("sp_profile_other_view_page", args=[self.username])

    def get_username(self):
        """Return the username"""
        custom_setting = getattr(settings, "SP_SET_USERNAME", False)
        if self.is_staff or custom_setting:
            return self.username
        return self.email or "<anonymous>"

    def get_email(self):
        """Return the email"""
        return self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between else email
        """
        full_name = f"{self.first_name} {self.last_name}"
        if full_name:
            return full_name.strip()
        return self.get_email()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def get_avatar_img(self):
        """
        Returns the short name for the user.
        """
        if self.image_avatar:
            return "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"

        if self.image_avatar == "socials":
            if self.google_avatar:
                return self.google_avatar
            elif self.twitter_avatar:
                return self.twitter_avatar
            elif self.facebook_avatar:
                return self.facebook_avatar
            elif self.instagram_avatar:
                return self.instagram_avatar
            else:
                return static(f"{self.image}")

        elif self.image_avatar == "predef":
            return static(f"socialprofile/img/avatar/{self.image_avatar_predef}")

        else:
            return static(f"{self.image}")

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class SocialProfile(AbstractSocialProfile):
    """
    Concrete class of AbstractSocialProfile.
    Use this if you don't need to extend SocialProfile.
    """

    class Meta(AbstractSocialProfile.Meta):  # noqa: D101
        swappable = "AUTH_USER_MODEL"


# def __str__(self):
#     return "{}".format(self.group.name)
#
# group = models.OneToOneField('auth.Group', unique=True, parent_link=True, on_delete=models.CASCADE)


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

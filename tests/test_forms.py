"""Unit Tests for the socialprofile module forms"""

# pylint: disable=R0904, C0103

import logging

from django.forms.models import model_to_dict
from django.test import TestCase
from social.apps.django_app.default.models import UserSocialAuth

from socialprofile.forms import SocialProfileForm
from socialprofile.models import SocialProfile

LOGGER = logging.getLogger(name="socialprofile.test_forms")


class SocialProfileFormTestCase(TestCase):
    """Test Case for Social Profile Forms"""

    def setUp(self):
        """Set up common assets for tests"""
        LOGGER.debug("SocialProfileForm Tests setUp")
        self.user1 = SocialProfile.objects.create_user(
            "user1@user1.com",
            username="user1",
        )
        self.user1.set_password("user1password")
        # todo: check because is not rendered as field inside forms
        self.user1.username = "user1"
        self.user1.gender = "other"
        self.user1.url = "http://test.com"
        self.user1.description = "Test User 1"
        self.user1.image_url = (
            "http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        )
        self.user1.save()
        self.sa1 = UserSocialAuth.objects.create(
            user=self.user1, provider="google-oauth2", uid="user1@user1.com"
        )

    def test_socialprofile_form_view(self):
        """Test editing user profile data through form in isolation"""
        LOGGER.debug("Test socialprofile edit form")
        form = SocialProfileForm(instance=self.user1)
        form_html = form.as_p()
        LOGGER.debug(form_html)
        # self.assertInHTML(
        #     '<option value="other" selected="selected">Other</option>', form_html
        # )
        self.assertInHTML(
            '<input id="id_returnTo" name="returnTo" type="hidden" value="/" />',
            form_html,
        )
        self.assertInHTML(
            '<textarea cols="40" id="id_description" name="description" rows="10">Test User 1</textarea>',
            form_html,
        )
        # self.assertInHTML(
        #     '<input id="id_image_url" maxlength="500" name="image_url" type="url" value="http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm" />',
        #     form_html,
        # )
        # self.assertInHTML(
        #     '<input id="id_manually_edited" name="manually_edited" type="hidden" value="True" />',
        #     form_html,
        # )
        self.assertInHTML(
            '<input id="id_url" maxlength="500" name="url" type="url" value="http://test.com" />',
            form_html,
        )

    def test_socialprofile_form_update(self):
        """Test Form Update"""
        LOGGER.debug("Test socialprofile edit form")
        data = model_to_dict(self.user1)
        data["description"] = "new description"
        data["gender"] = "female"
        data["url"] = "http://new.url/"
        data["image_url"] = "http://new.image.url/"
        # data["country"] = 'en' # Raise error
        data["country"] = "IT"
        form = SocialProfileForm(data=data, instance=self.user1)
        if not form.is_valid():
            LOGGER.error(form.errors)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.user1.description, "new description")
        self.assertEqual(self.user1.url, "http://new.url/")
        self.assertEqual(self.user1.gender, "female")
        # self.assertEqual(self.user1.image_url, "http://new.image.url/")

    def test_socialprofile_form_clean_desc(self):
        """Test Form Clean"""
        LOGGER.debug("Test socialprofile form clean desc")
        data = model_to_dict(self.user1)
        data["description"] = '<a href="http://bad.url">Bad Link</a>'
        data["gender"] = "female"
        form = SocialProfileForm(data=data, instance=self.user1)
        if not form.is_valid():
            LOGGER.error(form.errors)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.user1.description, "Bad Link")


#
# class UserFormTestCase(TestCase):
#         """Tests for  User Form"""
#
#     def setUp(self):
#         """Set up common assets for tests"""
#         LOGGER.debug("UserForm Tests setUp")
#         self.user1 = User.objects.create_user('user1', 'user1@user1.com', 'user1password')
#
#     def test_user_form_create(self):
#         LOGGER.debug("Test user form create")
#         data = {
#         'username': 'user2',
#         'password': 'user2password',
#         'email': 'user@user2.com',
#         'first_name': 'user',
#         'last_name': '2',
#         'last_login': '2012-09-04 06:00',
#         'date_joined': '2012-09-04 06:00',
#         'manually_edited': False
#         }
#         form = UserForm(data)
#         self.assertTrue(form.is_valid())
#         form.save()
#         user2 = User.objects.get(username='user2')
#         self.assertEquals(user2.username, 'user2')
#
#     def test_user_form_view(self):
#         """Test editing user profile data through form in isolation"""
#         LOGGER.debug("Test user edit form")
#         form = UserForm(instance=self.user1)
#         form_html = form.as_p()
#         LOGGER.debug(form_html)
#         self.assertInHTML('<input id="id_username" maxlength="30" name="username" type="text" value="user1" />', form_html)
#         self.assertInHTML('<input id="id_first_name" maxlength="30" name="first_name" type="text" />', form_html)
#         self.assertInHTML('<input id="id_email" maxlength="75" name="email" type="email" value="user1@user1.com" />', form_html)
#         self.assertInHTML('<input id="id_last_name" maxlength="30" name="last_name" type="text" />', form_html)
#         self.assertNotIn('<input id="id_is_staff" name="is_staff" type="checkbox" />', form_html)
#         self.assertNotIn('<input checked="checked" id="id_is_active" name="is_active" type="checkbox" />', form_html)
#
#     def test_user_form_dupe_username(self):
#         LOGGER.debug("Test user form update")
#         data = {
#         'username': 'user1',
#         'password': 'user2password',
#         'email': 'user@user2.com',
#         'first_name': 'user',
#         'last_name': '2',
#         'last_login': '2012-09-04 06:00',
#         'date_joined': '2012-09-04 06:00',
#         'manually_edited': False
#         }
#         form = UserForm(data)
#         self.assertIn('already exists', form.errors['username'][0])
#
#     def test_user_form_update(self):
#         LOGGER.debug("Test user form create")
#         data = {
#         'username': 'user1',
#         'first_name': 'user',
#         'last_name': 'Two',
#         'last_login': '2012-09-04 06:00',
#         'date_joined': '2012-09-04 06:00',
#         'manually_edited': False
#         }
#         form = UserForm(data, instance=self.user1)
#         self.assertTrue(form.is_valid())
#         form.save()
#         self.assertEquals(self.user1.last_name, 'Two')

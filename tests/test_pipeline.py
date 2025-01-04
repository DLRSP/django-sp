"""Unit Tests for the socialprofile module forms"""

import logging

from django.test import TestCase
from social_core.backends.google import GoogleOAuth2
from social_core.backends.twitter import TwitterOAuth
from social_core.backends.facebook import FacebookOAuth2

from socialprofile.models import SocialProfile
from socialprofile.pipeline import socialprofile_extra_values

LOGGER = logging.getLogger(name="socialprofile.test_pipeline")


class SocialProfilePipelineTestCase(TestCase):
    """Test Case for Social Profile Pipeline"""

    def setUp(self):
        """Set up common assets for tests"""
        LOGGER.debug("SocialProfile Pipeline Tests setUp")
        self.user1 = SocialProfile.objects.create_user(
            "user1@user1.com", "mypassword", "user1"
        )
        self.user1.description = "Test User 1"
        self.user1.gender = "other"
        self.user1.url = "http://test.url"

        self.user1.google_url = "http://test.url"
        self.user1.google_avatar = (
            "http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        )

        self.user1.twitter_url = "http://test.url"
        self.user1.twitter_avatar = (
            "http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        )

        self.user1.instagram_url = "http://test.url"
        self.user1.instagram_avatar = (
            "http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        )

        self.user1.facebook_url = "http://test.url"
        self.user1.facebook_avatar = (
            "http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        )
        self.user1.save()

    # self.sa1 = UserSocialAuth.objects.create(user=self.user1, provider='google-oauth2', uid='user1@user1.com')
    def test_socialprofile_pipeline_google(self):
        """Test editing executing pipeline methods in isolation for google"""
        LOGGER.debug("Test socialprofile pipeline Google")
        backend = GoogleOAuth2()
        response = {
            "name": {"familyName": "User 1", "givenName": "Test"},
            "gender": "other",
            "picture": "http://image-google.url",
            "occupation": "User Description",
            "url": "http://google.url",
        }

        socialprofile_extra_values(backend, {}, response, "1", self.user1)
        self.assertTrue(self.user1.edited_by_google)
        self.assertEqual(self.user1.description, "User Description")
        self.assertEqual(self.user1.gender, "other")
        self.assertEqual(self.user1.google_avatar, "http://image-google.url")
        self.assertEqual(self.user1.google_url, "http://google.url")

    def test_socialprofile_pipeline_facebook(self):
        """Test editing executing pipeline methods in isolation for facebook"""
        LOGGER.debug("Test socialprofile pipeline Facebook")
        backend = FacebookOAuth2()
        response = {
            "name": {"last_name": "User 1", "first_name": "Test"},
            "gender": "other",
            "picture": {"data": {"url": "http://image-facebook.url"}},
            "link": "http://facebook.url",
        }

        socialprofile_extra_values(backend, {}, response, "1", self.user1)
        self.assertTrue(self.user1.edited_by_facebook)
        self.assertEquals(self.user1.gender, "other")
        self.assertEquals(self.user1.facebook_avatar, "http://image-facebook.url")
        self.assertEquals(self.user1.facebook_url, "http://facebook.url")

    def test_socialprofile_pipeline_twitter(self):
        """Test editing executing pipeline methods in isolation for twitter"""
        LOGGER.debug("Test socialprofile pipeline Twitter")
        backend = TwitterOAuth()
        response = {
            "name": {"last_name": "User 1", "first_name": "Test"},
            "gender": "other",
            "profile_image_url_https": "http://image-twitter.url",
            "description": "User Description",
            "url": "http://twitter.url",
        }

        socialprofile_extra_values(backend, {}, response, "1", self.user1)
        self.assertTrue(self.user1.edited_by_twitter)
        self.assertEqual(self.user1.description, "User Description")
        self.assertEqual(self.user1.gender, "other")
        self.assertEqual(self.user1.twitter_avatar, "http://image-twitter.url")
        self.assertEqual(self.user1.twitter_url, "http://twitter.url")

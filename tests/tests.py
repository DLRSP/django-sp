"""Unit Tests for the socialprofile module"""

# pylint: disable=R0904, C0103

import logging

from django.test import TestCase

from socialprofile.models import SocialProfile

LOGGER = logging.getLogger(name="socialprofile")


class SocialProfileTestCase(TestCase):
    """Test Case for Social Profile"""

    def setUp(self):
        """Set up common assets for tests"""
        LOGGER.debug("SocialProfile Tests setUp")
        self.user1 = SocialProfile.objects.create_user(
            "user1", "user1@user1.com", "user1password"
        )
        self.user1.gender = "unknown"
        self.user1.url = "http://test.com"
        self.user1.description = "Test User 1"
        self.user1.image_url = (
            "http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        )
        self.user1.save()
        # self.sp1 = SocialProfile.objects.update(id=self.user1,
        # gender="Male",
        # url="http://test.com",
        # description="Test User 1",
        # image_url="http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        # )
        # self.sa1 = UserSocialAuth.objects.create(user=self.user1, provider='google-oauth2', uid='user1@user1.com')
        # self.sa2 = UserSocialAuth.objects.create(user=self.user1, provider='facebook', uid='user1@user1.com')
        # self.sa2 = UserSocialAuth.objects.create(user=self.user1, provider='twitter', uid='user1@user1.com')

    def tearDown(self):
        """Remove Test Data"""
        LOGGER.debug("SocialProfile Tests tearDown")
        self.user1.delete()

    # def test_redirect_urls(self):
    # """Test that redirects kicking in when trying to go to secure page."""
    # LOGGER.debug("SocialProfile Test Redirect URLs")
    # response = self.client.get('/secure/', follow=True)
    # self.assertRedirects(response, "http://testserver/sp/select/?next=/secure/")
    #
    # def test_view_profile(self):
    # """Test to see if profile for user1 can be viewed anon and logged in"""
    # LOGGER.debug("Test GET /sp/view/user1/ for anon user")
    # anon_view_response = self.client.get('/sp/view/user1/')
    # self.assertContains(anon_view_response, "Test User 1")
    #
    # LOGGER.debug("Test GET /sp/ for anon user")
    # anon_view_generic_response = self.client.get('/sp/')
    # self.assertEqual(404, anon_view_generic_response.status_code)
    #
    # LOGGER.debug("Test GET /sp/view/ for anon user")
    # anon_view_generic_response_2 = self.client.get('/sp/view/')
    # self.assertEqual(404, anon_view_generic_response_2.status_code)
    #
    # LOGGER.debug("Test GET /sp/view/user1/ for logged in user")
    # self.client.login(username='user1', password='user1password')
    # logged_in_view_response = self.client.get('/sp/view/user1/')
    # self.assertContains(logged_in_view_response, "Test User 1")
    #
    # LOGGER.debug("Test GET /sp/ for logged in user")
    # logged_in_view_generic_response = self.client.get('/sp/')
    # self.assertContains(logged_in_view_generic_response, "Test User 1")
    #
    # LOGGER.debug("Test GET /sp/view/ for logged in user")
    # logged_in_view_generic_response_2 = self.client.get('/sp/view/')
    # self.assertEqual(404, logged_in_view_generic_response_2.status_code)
    #
    # LOGGER.debug("Test GET /sp/view/ for logged in user")
    # logged_in_view_generic_response_2 = self.client.get('/sp/view/')
    # self.assertEqual(404, logged_in_view_generic_response_2.status_code)
    #
    # LOGGER.debug("Test POST to /sp/view/ for logged in user")
    # logged_in_view_post_response = self.client.post('/sp/', {'user': 1}, follow=True)
    # self.assertEqual(405, logged_in_view_post_response.status_code)  # HTTP POST Not Allowed
    #
    # def test_socialprofile_permalink(self):
    # """Test the permalink method of SocialProfile"""
    # LOGGER.debug("Test SocialProfile Permalink")
    # profile = SocialProfile.objects.get(id=self.user1.id)
    # permalink = profile.get_absolute_url()
    # self.assertEqual("/sp/view/user1/", permalink)
    # anon_view_response = self.client.get(permalink)
    # self.assertContains(anon_view_response, "Test User 1")
    #
    # def test_edit_profile(self):
    # """Test to see if profile for user1 can be edited anon and logged in"""
    # LOGGER.debug("Test GET /sp/edit/user1/ for anon user")
    # anon_edit_response = self.client.get('/sp/edit/user1/')
    # self.assertEqual(404, anon_edit_response.status_code)
    #
    # LOGGER.debug("Test GET /sp/edit/ for anon user")
    # anon_edit_response_2 = self.client.get('/sp/edit/')
    # self.assertRedirects(anon_edit_response_2, "http://testserver/sp/select/?next=/sp/edit/")
    #
    # LOGGER.debug("Test POST /sp/edit/ for anon user")
    # anon_edit_response_2 = self.client.post('/sp/edit/', {'user': 1}, follow=True)
    # self.assertRedirects(anon_edit_response_2, "http://testserver/sp/select/?next=/sp/edit/")
    #
    # LOGGER.debug("Test GET /sp/edit/user1/ for logged in user")
    # self.client.login(username='user1', password='user1password')
    # anon_edit_response = self.client.get('/sp/edit/user1/')
    # self.assertEqual(404, anon_edit_response.status_code)
    #
    # LOGGER.debug("Test GET /sp/edit/ for logged in user")
    # logged_in_edit_response = self.client.get('/sp/edit/')
    # self.assertContains(logged_in_edit_response, "Test User 1")
    #
    # LOGGER.debug("Test POST /sp/edit/ for logged in user")
    # post_data = {
    # 'user': 1,
    # 'username': 'user2',
    # 'email': 'user1@test.com',
    # 'first_name': 'Test',
    # 'last_name': 'User',
    # 'description': "Test1 User",
    # 'image_url': 'http://foo.com',
    # 'url': 'http://user1.com',
    # 'returnTo': '/secure/'
    # }
    # logged_in_edit_response_2 = self.client.post('/sp/edit/', post_data, follow=True)
    # self.assertContains(logged_in_edit_response_2, "updated")
    # user = SocialProfile.objects.get(username='user2')
    # self.assertEqual('user2', str(user.social_profile))
    #
    # LOGGER.debug("Test Invalid Form Error")
    # post_data = {
    # 'username': 'user2',
    # 'email': 'user1@test.com',
    # 'gender': 'Robot',
    # 'first_name': 'Test',
    # 'last_name': 'User',
    # 'description': "Test1 User",
    # 'image_url': 'http://foo.com',
    # 'url': 'http://user1.com',
    # 'returnTo': '/secure/'
    # }
    # logged_in_edit_response_3 = self.client.post('/sp/edit/', post_data, follow=True)
    # self.assertContains(logged_in_edit_response_3, "NOT")
    #
    # def test_delete_user(self):
    # """Test the views that enable deleting users/socialprofiles"""
    # LOGGER.debug("Test GET /sp/delete/ for logged in user")
    # self.client.login(username='user1', password='user1password')
    # logged_in_delete_response = self.client.get('/sp/delete/')
    # self.assertContains(logged_in_delete_response, "Really Delete")
    #
    # LOGGER.debug("Test POST to /sp/delete/ for logged in user")
    # logged_in_delete_post_response = self.client.post('/sp/delete/', {'user': 1}, follow=True)
    # self.assertRedirects(logged_in_delete_post_response, '/')
    #
    # LOGGER.debug("Test GET /sp/view/user1/ for deleted user")
    # deleted_response = self.client.get('/sp/view/user1/')
    # LOGGER.debug(deleted_response)
    # self.assertEqual(404, deleted_response.status_code)

"""Python Social Auth Pipeline Extensions"""

from social.backends.google import GoogleOAuth2
from social.backends.twitter import TwitterOAuth
from social.backends.facebook import Facebook2OAuth2


def socialprofile_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Routes the extra values call to the appropriate back end"""
    if type(backend) is GoogleOAuth2:
        google_extra_values(backend, details, response, uid, user, *args, **kwargs)

    if type(backend) is TwitterOAuth:
        twitter_extra_values(backend, details, response, uid, user, *args, **kwargs)

    if type(backend) is Facebook2OAuth2:
        facebook_extra_values(backend, details, response, uid, user, *args, **kwargs)


def google_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Google Auth"""
    if not user.manually_edited:
        user.last_name = response.get('name').get('familyName', '')
        user.first_name = response.get('name').get('givenName', '')
        user.save()

        user.gender = response.get('gender', '')
        user.image_url = response.get('image').get('url', '')
        user.url = response.get('url', '')
        user.description = response.get('occupation', '')

        user.save()


def facebook_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Facebook Auth"""
    if not user.manually_edited:
        user.last_name = response.get('last_name', '')
        user.first_name = response.get('first_name', '')
        user.save()

        user.gender = response.get('gender', '')
        user.url = response.get('link', '')
        if response.get('picture', False):
            user.image_url = response.get('picture').get('data').get('url', '')

        user.save()

    return response


def twitter_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Twitter Auth"""
    if not user.manually_edited:
        try:
            first_name, last_name = response.get('name', '').split(' ', 1)
        except:
            first_name = response.get('name', '')
            last_name = ''
        user.last_name = last_name
        user.first_name = first_name
        user.save()

        user.url = response.get('url', '')
        user.image_url = response.get('profile_image_url_https', '')
        user.description = response.get('description', '')

        user.save()

    return response
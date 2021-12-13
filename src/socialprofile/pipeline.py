"""Python Social Auth Pipeline Extensions"""

from social_core.backends.facebook import FacebookOAuth2 as FacebookOAuth2
from social_core.backends.google import GoogleOAuth2 as GoogleOAuth2
from social_core.backends.twitter import TwitterOAuth as TwitterOAuth
from requests import request


# def create_profile(user, is_new=False, *args, **kwargs):
#     """Create a profile instance for the given user"""
#     if is_new:
#         profile = user.get_profile()
#         if profile is None:
#             profile = Profile(user_id=user.id)
#         profile.gender = response.get("gender")
#         profile.link = response.get("link")
#         profile.timezone = response.get("timezone")
#         profile.save()


def socialprofile_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Routes the extra values call to the appropriate back end"""
    if type(backend) is GoogleOAuth2:
        return {
            "user": google_extra_values(
                backend, details, response, uid, user, *args, **kwargs
            )
        }

    if type(backend) is TwitterOAuth:
        return {
            "user": twitter_extra_values(
                backend, details, response, uid, user, *args, **kwargs
            )
        }

    if type(backend) is FacebookOAuth2:
        return {
            "user": facebook_extra_values(
                backend, details, response, uid, user, *args, **kwargs
            )
        }


def google_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Google Auth"""
    # ToDo: should be placed in new pipeline before
    # if kwargs.get("new_association"):
    #     print("is new google association!")
    #     try:
    #         req_response = request(
    #             "GET",
    #             "https://www.googleapis.com/oauth2/v3/userinfo",
    #             headers={
    #                 "Authorization": f"Bearer {kwargs.get('access_token')}",
    #             },
    #         ).json()
    #         print(req_response)
    #     except Exception as err:
    #         print(err)

    if not user.edited_by_user:
        user.last_name = response.get("family_name", "")
        user.first_name = response.get("given_name", "")
        user.save()

        date_of_birth = response.get("birthday")
        if date_of_birth:
            user.date_of_birth = date_of_birth
        gender = response.get("gender")
        if gender:
            user.gender = gender
        image_url = response.get("picture")
        if image_url:
            user.image_url = image_url
        country = response.get("locale")
        if country:
            user.country = country

    username_google = response.get("username")
    if username_google:
        user.username_facebook = username_google

    user.google_verified = response.get("email_verified", False)
    user.google_isPlusUser = response.get("isPlusUser", False)
    user.google_plusUrl = response.get("url", "")
    user.google_circledByCount = response.get("circledByCount", 0)
    user.google_language = response.get("language", "")
    user.google_kind = response.get("kind", "")

    user.edited_by_provider = True
    user.save()
    return user


def facebook_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Facebook Auth"""
    if not user.edited_by_user:
        user.last_name = response.get("last_name", "")
        user.first_name = response.get("first_name", "")
        user.save()

        gender = response.get("gender")
        if gender:
            user.gender = gender

    username_facebook = response.get("username")
    if username_facebook:
        user.username_facebook = username_facebook
    profile_url = response.get("link")
    if profile_url:
        user.facebook_url = profile_url
    if response.get("picture", False):
        user.image_url = response.get("picture").get("data").get("url", "")
    user.save()
    return user


def twitter_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Twitter Auth"""
    if not user.edited_by_user:
        try:
            first_name, last_name = response.get("name", "").split(" ", 1)
        except:
            first_name = response.get("name", "")
            last_name = ""
        user.last_name = last_name
        user.first_name = first_name
        user.save()

        image_url = response.get("profile_image_url_https")
        if image_url:
            user.image_url = image_url
        description = response.get("description")
        if description:
            user.description = description

    username_twitter = response.get("username")
    if username_twitter:
        user.username_twitter = username_twitter
    profile_url = response.get("url")
    if profile_url:
        user.twitter_url = profile_url
    user.twitter_language = response.get("lang", "")
    user.twitter_verified = response.get("verified", False)
    user.edited_by_provider = True

    user.save()
    return user

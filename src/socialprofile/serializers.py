from rest_framework import serializers

from socialprofile.models import SocialProfile


# Serializers define the API representation.
class SocialProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SocialProfile
        fields = ("url", "username", "email", "is_staff")

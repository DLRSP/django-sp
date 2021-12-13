from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import SocialProfile


@receiver(post_delete, sender=SocialProfile)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user:  # just in case user is not specified
        instance.user.delete()

from django.conf import settings
from django.core.mail import mail_admins, send_mail
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.html import strip_tags

from .models import SocialProfile


@receiver(post_delete, sender=SocialProfile)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user:  # just in case user is not specified
        instance.user.delete()


@receiver(post_save, sender=SocialProfile)
def post_save_user(sender, instance, created, *args, **kwargs):
    # ToDo: notify new user
    if created:
        # notify the admin
        mail_admins(f"New user [{instance.user}]", "New user was created!")

        # ToDo: notify the user with a welcome custom message
        html_mail = f"""<!DOCTYPE html><html><body>
                        <h1> Welcome!</h1>
                    """
        html_mail += f"""</body></html>"""
        plain_message = strip_tags(html_mail)
        send_mail(
            f"Welcome {instance.user}!",
            plain_message,
            html_message=html_mail,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=instance.user.email,
        )

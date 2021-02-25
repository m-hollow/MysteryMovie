from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from movies.models import UserProfile


# using a Signal to create a UserProfile for a user, everytime a new user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance) # create will automatically save the record in the db

# we need the UserProfile to be saved anytime the User model is saved, not just the first time it's created...
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

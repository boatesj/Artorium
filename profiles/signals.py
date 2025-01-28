from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile whenever a User object is saved.
    """
    if created:
        # Check if the role was set during registration
        role = getattr(instance, 'signup_role', 'patron')  # Default to patron if role is not provided
        UserProfile.objects.create(user=instance, role=role)
    else:
        # Update the profile if it already exists
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        if instance.is_superuser:
            profile.role = 'admin'
        profile.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile whenever a User object is saved.
    """
    if created:
        # ✅ Fix: Use `get_or_create` to prevent duplicates
        UserProfile.objects.get_or_create(user=instance, defaults={'role': getattr(instance, 'signup_role', 'patron')})
    else:
        # ✅ Fix: Only update the profile if it already exists
        try:
            profile = UserProfile.objects.get(user=instance)
            if instance.is_superuser:
                profile.role = 'admin'
            profile.save()
        except UserProfile.DoesNotExist:
            pass  # Prevents creation if no profile exists

@receiver(user_signed_up)
def create_user_profile(request, user, **kwargs):
    role = request.POST.get('role', 'patron')
    UserProfile.objects.create(user=user, role=role)

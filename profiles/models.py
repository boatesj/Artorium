from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    Handles role distinction and additional data for patrons and artists.
    """

    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('artist', 'Artist'),
    ]

    # Basic user and role data
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patron')
    is_admin = models.BooleanField(default=False)

    # Common fields for all users
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country *', null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)

    # Artist-specific fields
    artist_bio = models.TextField(null=True, blank=True)
    portfolio_link = models.URLField(max_length=200, null=True, blank=True)
    is_available_for_commissions = models.BooleanField(default=True)

    # Patron-specific fields
    wishlist = models.ManyToManyField('Artwork', blank=True, related_name='wishlisted_by')

    def __str__(self):
        return self.user.username


class Artwork(models.Model):
    """
    Artwork model for creating, updating, and managing artwork entries.
    """
    artist = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='artworks')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_featured = models.BooleanField(default=False)  # Highlight featured artworks
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Commission(models.Model):
    """
    Model to manage artwork commissions between patrons and artists.
    """
    patron = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='commissions_requested')
    artist = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='commissions_received')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    progress = models.TextField(null=True, blank=True)  # Track progress (e.g., "50% complete")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.artist.user.username} for {self.patron.user.username}"


class Transaction(models.Model):
    """
    Model to track transactions for admins and patrons.
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transactions')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, null=True, blank=True)
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction by {self.user.user.username} on {self.transaction_date}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile whenever a User object is saved.
    """
    if created:
        # Create a new UserProfile only if the user is newly created
        UserProfile.objects.create(user=instance)
    else:
        # Check if the profile exists before trying to save it
        UserProfile.objects.get_or_create(user=instance)
        # Save the profile for updates
        instance.userprofile.save()


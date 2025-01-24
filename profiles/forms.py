from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    """
    Form to update user profile information.
    """
    class Meta:
        model = UserProfile
        fields = [
            'default_phone_number',
            'default_country',
            'default_postcode',
            'default_town_or_city',
            'default_street_address1',
            'default_street_address2',
            'default_county',
            'artist_bio',
            'portfolio_link',
            'is_available_for_commissions',
        ]

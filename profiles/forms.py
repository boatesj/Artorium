from django import forms
from .models import UserProfile
from allauth.account.forms import SignupForm


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels, and set autofocus on first field
        """
        self.role = kwargs.pop('role', 'patron')  # Default role is patron
        super().__init__(*args, **kwargs)

        placeholders = {
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        self.fields['default_phone_number'].widget.attrs['autofocus'] = True

        for field in self.fields:
            if field != 'default_country':
                placeholder = placeholders.get(field, '')
                if self.fields[field].required:
                    placeholder += ' *'
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'
            self.fields[field].label = False


class CustomSignupForm(SignupForm):
    """
    Extend allauth's SignupForm to include role selection
    """
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('artist', 'Artist'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Register as")

    def save(self, request):
        """
        Save user with the selected role
        """
        user = super().save(request)
        # Attach the role to the user instance, to be used in the profile creation logic
        user.signup_role = self.cleaned_data['role']  # Add signup_role attribute dynamically
        return user

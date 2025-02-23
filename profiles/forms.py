from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Transaction
from allauth.account.forms import SignupForm



class UserProfileForm(forms.ModelForm):
    """
    Form to edit user profile details
    """
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('artist', 'Artist'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Register as")

    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders, classes, and autofocus settings
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
            'artist_bio': 'Artist Biography',
            'portfolio_link': 'Portfolio Website'
        }

        self.fields['default_phone_number'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field in placeholders:
                placeholder = placeholders[field]
                if self.fields[field].required:
                    placeholder += ' *'
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'
            self.fields[field].label = False


class RoleSignupForm(SignupForm):
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('artist', 'Artist'),
    ]
    
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Register as")

    def save(self, request):
        """ Extend Allauth's save method to include the role """
        user = super(RoleSignupForm, self).save(request)  # Save the user first
        role = self.cleaned_data['role']

        # 🔥 Check if the user already has a profile before creating one
        profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': role})

        return user


class TransactionForm(forms.ModelForm):
    """
    Form to create or edit a transaction, excluding the transaction_date field.
    """
    class Meta:
        model = Transaction
        exclude = ['transaction_date']  # Exclude the non-editable field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['class'] = 'form-control'
        self.fields['amount'].widget.attrs['placeholder'] = 'Enter the transaction amount'
        self.fields['amount'].widget.attrs['class'] = 'form-control'

# class CommissionForm(forms.ModelForm):
#     """
#     Form to create or edit a commission.
#     """
#     class Meta:
#         model = Commission
#         fields = ['title', 'artist', 'patron', 'is_approved', 'is_declined']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['title'].widget.attrs['placeholder'] = 'Enter the title of the commission'
#         self.fields['title'].widget.attrs['class'] = 'form-control'
#         self.fields['artist'].widget.attrs['class'] = 'form-control'
#         self.fields['patron'].widget.attrs['class'] = 'form-control'
#         self.fields['is_approved'].widget.attrs['class'] = 'form-check-input'
#         self.fields['is_declined'].widget.attrs['class'] = 'form-check-input'


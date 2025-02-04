from django import forms
from .models import UserProfile, Transaction


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



class CustomSignupForm(forms.Form):
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
        from allauth.account.forms import SignupForm  # Lazy import inside the method
        from django.db.utils import IntegrityError
        from django.contrib import messages

        user = SignupForm.save(self, request)  # Save the user first using the superclass method
        try:
            UserProfile.objects.create(user=user, role=self.cleaned_data['role'])  # Create the user profile with the role
        except IntegrityError:
            existing_profile = UserProfile.objects.get(user=user)
            messages.warning(request, 'UserProfile already exists. Using existing profile.')

        return user



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

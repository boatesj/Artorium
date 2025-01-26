from django import forms
from .models import Artwork, Category



class ArtworkForm(forms.ModelForm):
    """
    Form for creating and managing artworks.
    """

    class Meta:
        model = Artwork
        fields = '__all__'  # Include all fields from the Artwork model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        # Update category choices with friendly names
        self.fields['category'].choices = friendly_names

        # Add consistent styling to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'


    

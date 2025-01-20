from django.contrib import admin
from .models import Artwork, Category

# Register your models here.

class ArtworkAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'artist',
        'get_categories',
        'price',
        'available',
        'image',
    )

    ordering = ('title',)

    def get_categories(self, obj):
        """ Return a comma-separated list of categories for the artwork """
        return ", ".join([cat.friendly_name for cat in obj.category.all()])
    
    get_categories.short_description = 'Categories'

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

admin.site.register(Artwork, ArtworkAdmin)
admin.site.register(Category, CategoryAdmin)

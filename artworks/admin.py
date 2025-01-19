from django.contrib import admin
from .models import Artwork, Category

# Register your models here.

class ArtworkAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'artist',
        'category',
        'price',
        'available',
        'image',
    )

    ordering = ('title',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

admin.site.register(Artwork, ArtworkAdmin)
admin.site.register(Category, CategoryAdmin)

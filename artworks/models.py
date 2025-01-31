from django.db import models
from django.apps import apps

class Category(models.Model):
    """ Categories for artwork classification """
    
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254, unique=True)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Artwork(models.Model):
    """ Unified Artwork model for all artworks """

    category = models.ManyToManyField('Category', blank=True, related_name='artworks')
    title = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    artist = models.ForeignKey(
        "profiles.UserProfile",
        on_delete=models.SET_NULL,  # Set artist to NULL if not provided
        null=True, blank=True  # Allow NULL values
    )
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(upload_to='artworks/', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    available = models.BooleanField(default=True)
    sku = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_featured = models.BooleanField(default=False)  # Keep from profiles version

    def __str__(self):
        return self.title

    def get_categories(self):
        """ Return all categories assigned to this artwork as a list """
        return self.category.all()
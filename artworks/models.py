from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Artwork(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    artist = models.CharField(max_length=254, null=True, blank=True)
    image = models.ImageField(upload_to='artworks/', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

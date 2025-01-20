from django.shortcuts import render, redirect, reverse, get_object_or_404 
from django.contrib import messages
from django.db.models import Q
from .models import Artwork, Category

# Create your views here.

def all_artworks(request):
    """ A view to show all artworks, including sorting and search queries """

    artworks = Artwork.objects.all()
    query = None
    categories = None

    if request.GET:
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            artworks = artworks.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('artworks'))
            
            queries = Q(title__icontains=query) | Q(description__icontains=query) | Q(artist__icontains=query)
            artworks = artworks.filter(queries)

    context = {
        'artworks': artworks,
        'search_term': query,
        'current_categories': categories,
    }

    return render(request, 'artworks/artworks.html', context)


def artwork_detail(request, artwork_id):
    """ A view to show individual artwork details """

    artwork = get_object_or_404(Artwork, pk=artwork_id)

    context = {
        'artwork': artwork,
    }

    return render(request, 'artworks/artwork_detail.html', context)

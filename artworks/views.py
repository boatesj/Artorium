from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Artwork, Category
from .forms import ArtworkForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def all_artworks(request):
    """ A view to show all artworks, including sorting and search queries """

    artworks = Artwork.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        # Sorting logic
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'title':  # Sort by artwork title
                sortkey = 'lower_title'
                artworks = artworks.annotate(lower_title=Lower('title'))
            if sortkey == 'category':  # Sort by category name
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            artworks = artworks.order_by(sortkey)

        # Filtering by category
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            artworks = artworks.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        # Search logic
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('artworks'))

            queries = Q(title__icontains=query) | Q(description__icontains=query) | Q(artist__icontains=query)
            artworks = artworks.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'artworks': artworks,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'artworks/artworks.html', context)


def artwork_detail(request, artwork_id):
    """ A view to show individual artwork details """

    # Retrieve the specific artwork by ID
    artwork = get_object_or_404(Artwork, pk=artwork_id)

    context = {
        'artwork': artwork,  # Updated context key
    }

    # Render the appropriate template
    return render(request, 'artworks/artwork_detail.html', context)
    

@login_required
def add_artwork(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = request.user.userprofile  # Link artwork to the artist
            artwork.save()
            return redirect('all_artworks')
    else:
        form = ArtworkForm()

    return render(request, 'artworks/add_artwork.html', {'form': form})


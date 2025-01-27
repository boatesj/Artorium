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
    """ Add an artwork to the gallery """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only admin can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added artwork!')
            return redirect(reverse('add_artwork'))  # Redirect back to the add artwork page
        else:
            messages.error(request, 'Failed to add artwork. Please ensure the form is valid.')
    else:
        form = ArtworkForm()
        
    template = 'artworks/add_artwork.html'  # Update template path
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_artwork(request, artwork_id):
    """Edit an artwork to the gallery """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only admin can do that.')
        return redirect(reverse('home'))
    artwork = get_object_or_404(Artwork, id=artwork_id)
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            artwork = form.save()
            messages.success(request, 'Artwork updated successfully!')
            return redirect(reverse('artwork_detail', args=[artwork.id]))
        else:
            messages.error(request, 'Failed to update artwork. Please ensure the form is valid.')
    else:
        form = ArtworkForm(instance=artwork)
        messages.info(request, f'You are editing {artwork.title}')

    template = 'artworks/edit_artwork.html'
    context = {'form': form, 'artwork': artwork}
    return render(request, template, context)


@login_required
def delete_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, pk=artwork_id)
    if not request.user.is_superuser and request.user != artwork.artist.user:
        raise PermissionDenied("You do not have permission to delete this artwork.")
    artwork.delete()
    messages.success(request, 'Artwork deleted!')
    return redirect(reverse('artworks'))

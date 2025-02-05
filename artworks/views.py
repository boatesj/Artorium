from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q, F
from django.db.models.functions import Lower
from .models import Artwork, Category
from .forms import ArtworkForm
from django.contrib.auth.decorators import login_required
from profiles.models import UserProfile



# Create your views here.

def all_artworks(request):
    """ A view to show all artworks, including sorting and search queries """

    artworks = Artwork.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'title':
                sortkey = 'title'
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            artworks = artworks.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            artworks = artworks.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('artworks'))
            queries = Q(title__icontains=query) | Q(description__icontains=query)
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
    artwork = get_object_or_404(Artwork, pk=artwork_id)

    context = {'artwork': artwork}
    return render(request, 'artworks/artwork_detail.html', context)


@login_required
def add_artwork(request):
    """ Add an artwork to the gallery """
    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.role != 'artist' and not request.user.is_superuser:
        messages.error(request, 'Only artists and admins can add artworks.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = profile if not request.user.is_superuser else None
            artwork.save()
            messages.success(request, 'Successfully added artwork!')
            return redirect(reverse('artworks'))
        else:
            messages.error(request, 'Failed to add artwork. Please check the form.')

    else:
        form = ArtworkForm()

    context = {'form': form}
    return render(request, 'artworks/add_artwork.html', context)


@login_required
def edit_artwork(request, artwork_id):
    """ Edit an artwork """
    artwork = get_object_or_404(Artwork, pk=artwork_id)
    profile = get_object_or_404(UserProfile, user=request.user)

    if not (request.user.is_superuser or artwork.artist == profile):
        messages.error(request, 'You do not have permission to edit this artwork.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artwork updated successfully!')
            return redirect(reverse('manage_portfolio'))
        else:
            messages.error(request, 'Failed to update artwork. Please check the form.')

    else:
        form = ArtworkForm(instance=artwork)
        messages.info(request, f'You are editing {artwork.title}')

    context = {'form': form, 'artwork': artwork}
    return render(request, 'artworks/edit_artwork.html', context)


@login_required
def delete_artwork(request, artwork_id):
    """ Delete an artwork """
    profile = get_object_or_404(UserProfile, user=request.user)
    artwork = get_object_or_404(Artwork, id=artwork_id)

    if not (request.user.is_superuser or artwork.artist == profile):
        raise PermissionDenied("You do not have permission to delete this artwork.")

    if request.method == 'POST':
        artwork.delete()
        messages.success(request, 'Artwork deleted successfully.')
        return redirect(reverse('artworks'))

    return render(request, 'artworks/delete_artwork.html', {'artwork': artwork})


@login_required
def add_artwork_artist(request):
    """ Allow artists to add new artwork from their dashboard """
    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.role != 'artist':
        messages.error(request, "You do not have permission to add artwork.")
        return redirect('artist_dashboard')

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = profile
            artwork.save()
            messages.success(request, "Artwork added successfully!")
            return redirect('artist_dashboard')
        else:
            messages.error(request, "Failed to add artwork. Please check the form.")

    else:
        form = ArtworkForm()

    context = {'form': form}
    return render(request, 'artworks/add_artwork_artist.html', context)


def artwork_list(request):
    """ Display a list of all artworks """
    artworks = Artwork.objects.all()
    return render(request, 'artworks/artwork_list.html', {'artworks': artworks})


@login_required
def manage_portfolio(request):
    """ Display all artworks uploaded by the logged-in artist """
    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.role != 'artist':
        messages.error(request, "Access Denied: Only artists can manage portfolios.")
        return redirect('home')

    artworks = Artwork.objects.filter(artist=profile)

    return render(request, 'profiles/manage_portfolio.html', {'artworks': artworks})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'artworks/category_list.html', {'categories': categories})


def artwork_list(request):
    artworks = Artwork.objects.all()
    return render(request, 'artworks/artwork_list.html', {'artworks': artworks})






    

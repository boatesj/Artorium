from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
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
    if request.user.userprofile.role != 'artist' and not request.user.is_superuser:
        messages.error(request, 'Sorry, only artists or admins can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = request.user.userprofile  # Set the logged-in artist as the creator
            artwork.save()
            messages.success(request, 'Successfully added artwork!')
            return redirect(reverse('artist_dashboard'))  # Redirect to artist dashboard
        else:
            messages.error(request, 'Failed to add artwork. Please ensure the form is valid.')
    else:
        form = ArtworkForm()

    template = 'artworks/add_artwork.html'
    context = {'form': form}
    return render(request, template, context)



@login_required
def edit_artwork(request, artwork_id):
    """ Edit an artwork """
    artwork = get_object_or_404(Artwork, pk=artwork_id)

    # ✅ Ensure only the correct artist or admin can edit the artwork
    if request.user.userprofile.role != 'artist' and not request.user.is_superuser:
        messages.error(request, 'Sorry, only artists or admins can edit artworks.')
        return redirect(reverse('home'))

    if artwork.artist != request.user.username and not request.user.is_superuser:

        messages.error(request, 'You do not have permission to edit this artwork.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artwork updated successfully!')
            return redirect(reverse('manage_portfolio'))  # ✅ Redirect to correct portfolio page
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
    """ Delete an artwork """
    artwork = get_object_or_404(Artwork, pk=artwork_id)

    # ✅ Ensure only the correct artist or admin can delete the artwork
    if artwork.artist.user != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this artwork.')
        return redirect(reverse('home'))

    artwork.delete()
    messages.success(request, 'Artwork deleted!')
    return redirect(reverse('manage_portfolio'))  # ✅ Redirect to portfolio page



@login_required
def add_artwork_artist(request):
    """Allow artists to add new artwork from their dashboard."""
    profile = UserProfile.objects.get(user=request.user)

    # Ensure only artists can access this view
    if profile.role != 'artist':
        messages.error(request, "You do not have permission to add artwork.")
        return redirect('artist_dashboard')

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form but do not commit to the database yet
            artwork = form.save(commit=False)
            # Associate the logged-in artist's profile
            artwork.artist = profile
            artwork.save()
            messages.success(request, "Artwork added successfully!")
            return redirect('artist_dashboard')
        else:
            messages.error(request, "Failed to add artwork. Please ensure the form is valid.")
    else:
        form = ArtworkForm()

    template = 'artworks/add_artwork_artist.html'
    context = {
        'form': form,
    }
    return render(request, template, context)



@login_required
def manage_portfolio(request):
    """ Display all artworks uploaded by the logged-in artist """
    profile = get_object_or_404(UserProfile, user=request.user)

    # ✅ Ensure only the logged-in artist can see their own artworks
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






    

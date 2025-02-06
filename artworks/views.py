from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q, F
from django.db.models.functions import Lower
from .models import Artwork, Category
from .forms import ArtworkForm
from django.contrib.auth.decorators import login_required
from profiles.models import UserProfile



# Create your views here.

def gallery_view(request):
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
                return redirect(reverse('artworks:gallery'))
            queries = Q(title__icontains=query) | Q(description__icontains=query)
            artworks = artworks.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'artworks': artworks,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }
    return render(request, 'artworks/gallery.html', context)


def artwork_detail_view(request, artwork_id):
    """ A view to show individual artwork details """
    artwork = get_object_or_404(Artwork, pk=artwork_id)
    context = {'artwork': artwork}
    return render(request, 'artworks/artwork_detail.html', context)


@login_required
def admin_add_artwork_view(request):
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
            return redirect(reverse('artworks:gallery'))
        else:
            messages.error(request, 'Failed to add artwork. Please check the form.')
    else:
        form = ArtworkForm()

    context = {'form': form}
    return render(request, 'artworks/admin/admin_add_artwork.html', context)



@login_required
def edit_artwork_view(request, artwork_id):
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
            return redirect(reverse('profiles:manage_portfolio'))
        else:
            messages.error(request, 'Failed to update artwork. Please check the form.')
    else:
        form = ArtworkForm(instance=artwork)
        messages.info(request, f'You are editing {artwork.title}')

    context = {'form': form, 'artwork': artwork}
    return render(request, 'artworks/admin/edit_artwork.html', context)


@login_required
def delete_artwork_view(request, artwork_id):
    """ Delete an artwork (only by superusers or the artwork owner) """
    
    # Check if artwork exists
    artwork = Artwork.objects.filter(id=artwork_id).first()
    
    if not artwork:
        messages.error(request, "Artwork not found or already deleted.")
        return redirect(reverse('artworks:gallery'))  # Redirect safely
    
    # Ensure the user has a profile
    profile = get_object_or_404(UserProfile, user=request.user)
    
    # Ensure only the artwork owner or a superuser can delete
    if not request.user.is_superuser and artwork.artist != profile:
        messages.error(request, "You do not have permission to delete this artwork.")
        raise PermissionDenied("You do not have permission to delete this artwork.")

    if request.method == 'POST':
        print(f"🛠 Deleting artwork {artwork.id}: {artwork.title}")  # Debugging
        artwork.delete()
        messages.success(request, 'Artwork deleted successfully.')
        
        # Redirect back to the gallery after deletion
        return redirect(reverse('artworks:gallery'))

    return render(request, 'artworks/admin/delete_artwork.html', {'artwork': artwork})



@login_required
def artist_add_artwork_view(request):
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
    return render(request, 'artworks/artist/artist_add_artwork.html', context)


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


def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'artworks/category_list.html', {'categories': categories})


def artwork_list(request):
    artworks = Artwork.objects.all()
    return render(request, 'artworks/artwork_list.html', {'artworks': artworks})






    

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import UserProfile, Commission, Transaction
from .forms import UserProfileForm
from checkout.models import Order
from artworks.models import Artwork


@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, role=getattr(profile, 'role', 'patron'))
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure the form is valid.')
    else:
        form = UserProfileForm(instance=profile, role=getattr(profile, 'role', 'patron'))

    orders = profile.orders.all() if hasattr(profile, 'orders') else []

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)


# Role-Specific Dashboards

@login_required
def admin_dashboard(request):
    """ Admin dashboard for managing the platform """
    if not request.user.is_superuser:
        raise PermissionDenied("You do not have access to this page.")

    artworks = Artwork.objects.all()
    patrons = UserProfile.objects.filter(role='patron')
    artists = UserProfile.objects.filter(role='artist')
    commissions = Commission.objects.all()  # Fetch all commissions
    transactions = Transaction.objects.all()  # Fetch all transactions

    template = 'profiles/admin_dashboard.html'
    context = {
        'artworks': artworks,
        'patrons': patrons,
        'artists': artists,
        'commissions': commissions,  # Add commissions
        'transactions': transactions,  # Add transactions
    }

    return render(request, template, context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import UserProfile, Artwork, Commission


@login_required
def artist_dashboard(request):
    """Artist dashboard for managing their own artworks and commissions."""

    # Get the user's profile
    profile = get_object_or_404(UserProfile, user=request.user)

    # Check if the user is an artist or a superuser
    if not profile.is_artist() and not request.user.is_superuser:
        # Redirect non-artists to the home page or another appropriate page
        return redirect('home')  # Change 'home' to the appropriate redirection name

    # Optimize queries with related data
    artworks = Artwork.objects.filter(artist=profile).select_related('artist')
    commissions = profile.commissions_received.all()  # Assuming prefetch isn't needed for a related manager

    # Additional stats for the dashboard
    artwork_count = artworks.count()
    commission_count = commissions.count()

    # Prepare the context
    template = 'profiles/artist_profile.html'
    context = {
        'profile': profile,
        'artworks': artworks,
        'commissions': commissions,
        'artwork_count': artwork_count,
        'commission_count': commission_count,
    }

    return render(request, template, context)



@login_required
def patron_dashboard(request):
    """ Patron dashboard for managing orders and wishlist """
    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.role != 'patron':
        raise PermissionDenied("You do not have access to this page.")

    orders = Order.objects.filter(user_profile=profile)
    wishlist = profile.wishlist.all()

    template = 'profiles/patron_profile.html'
    context = {
        'orders': orders,
        'wishlist': wishlist,
    }

    return render(request, template, context)


@login_required
def edit_profile(request):
    """
    View to edit user profile details.
    """
    profile = request.user.userprofile  # Fetch the UserProfile of the logged-in user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('patron_dashboard')  # Redirect to the patron dashboard or another page
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profiles/edit_profile.html', {'form': form})

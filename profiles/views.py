from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import UserProfile
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

    template = 'dashboard/admin_dashboard.html'
    context = {
        'artworks': artworks,
        'patrons': patrons,
        'artists': artists,
    }

    return render(request, template, context)


@login_required
def artist_dashboard(request):
    """ Artist dashboard for managing their own artworks and commissions """
    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.role != 'artist':
        raise PermissionDenied("You do not have access to this page.")

    artworks = Artwork.objects.filter(artist=profile)
    commissions = profile.commissions_received.all()

    template = 'dashboard/artist_dashboard.html'
    context = {
        'artworks': artworks,
        'commissions': commissions,
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

    template = 'dashboard/patron_dashboard.html'
    context = {
        'orders': orders,
        'wishlist': wishlist,
    }

    return render(request, template, context)

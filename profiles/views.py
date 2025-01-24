from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Commission, Artwork, Transaction
from .forms import UserProfileForm


@login_required
def profile(request):
    """
    Display the user's profile.
    Dynamically renders role-specific content for patrons, artists, and admins.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.role == 'patron':
        # For patrons: wishlist, commissions requested, and transactions
        wishlist = user_profile.wishlist.all()
        commissions = Commission.objects.filter(patron=user_profile)
        transactions = Transaction.objects.filter(user=user_profile)
        template = 'profiles/patron_profile.html'
        context = {
            'user_profile': user_profile,
            'wishlist': wishlist,
            'commissions': commissions,
            'transactions': transactions,
        }

    elif user_profile.role == 'artist':
        # For artists: artworks created, commissions received
        artworks = Artwork.objects.filter(artist=user_profile)
        commissions = Commission.objects.filter(artist=user_profile)
        template = 'profiles/artist_profile.html'
        context = {
            'user_profile': user_profile,
            'artworks': artworks,
            'commissions': commissions,
        }

    elif user_profile.is_admin:
        # Redirect admins to the admin dashboard
        return redirect('admin_dashboard')

    else:
        # Default profile view for users without a specific role
        messages.error(request, "Your profile role is undefined.")
        return redirect('home')

    return render(request, template, context)


@login_required
def admin_dashboard(request):
    """
    Display the admin dashboard.
    Provides an overview of all commissions, transactions, and artworks.
    """
    commissions = Commission.objects.all()
    artworks = Artwork.objects.all()
    transactions = Transaction.objects.all()

    template = 'profiles/admin_dashboard.html'
    context = {
        'commissions': commissions,
        'artworks': artworks,
        'transactions': transactions,
    }

    return render(request, template, context)


@login_required
def edit_profile(request):
    """
    Allow users to edit their profile information.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "There was an error updating your profile. Please check your inputs.")
    else:
        form = UserProfileForm(instance=user_profile)

    template = 'profiles/edit_profile.html'
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, template, context)

from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import UserProfile
from .forms import UserProfileForm


def profile(request):
    """ Display the user's profile. """
    # Safely get the user's profile
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        # Initialize the form with POST data and profile instance
        form = UserProfileForm(request.POST, instance=profile, role=getattr(profile, 'role', 'patron'))
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
    else:
        # Initialize the form for GET requests
        form = UserProfileForm(instance=profile, role=getattr(profile, 'role', 'patron'))

    # Fetch the user's orders (adjust this logic if orders are tied differently in Artorium)
    orders = profile.orders.all() if hasattr(profile, 'orders') else []

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)

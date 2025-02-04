from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from checkout.models import Order
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


from allauth.account.views import SignupView
from .models import UserProfile, Transaction
from .forms import UserProfileForm, CustomSignupForm
from checkout.models import Order
from artworks.models import Artwork


class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_valid(self, form):
        user = form.save(self.request)
        try:
            # Assign the selected role to the user profile
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'])
        except IntegrityError:
            existing_profile = UserProfile.objects.get(user=user)
            messages.warning(self.request, 'UserProfile already exists. Using existing profile.')

        return redirect(self.get_success_url())

signup_view = CustomSignupView.as_view()



@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure the form is valid.')
    else:
        form = UserProfileForm(instance=profile)

    orders = profile.orders.all() if hasattr(profile, 'orders') else []

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)


@login_required
def dashboard_view(request):
    """
    Redirects users to their respective dashboards based on their role.
    Ensures the user's role is correctly retrieved from the UserProfile model.
    """
    try:
        # Ensure the user has a profile
        user_profile = UserProfile.objects.get(user=request.user)

        # Redirect based on role
        if user_profile.role == "admin":
            return redirect("admin_dashboard")
        elif user_profile.role == "artist":
            return redirect("artist_dashboard")
        elif user_profile.role == "patron":
            return redirect("patron_dashboard")
        else:
            return render(request, "profiles/no_role.html", {"message": "Role not assigned"})

    except ObjectDoesNotExist:
        # If the user profile does not exist, handle gracefully
        return render(request, "profiles/no_role.html", {"message": "User profile not found. Please contact support."})



    


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
    """
    Admin dashboard for managing the platform
    """
    try:
        # Ensure only superusers can access this view
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have access to this page.")

        # ✅ Fetch all necessary data
        artworks = Artwork.objects.all()
        patrons = UserProfile.objects.filter(role='patron')
        artists = UserProfile.objects.filter(role='artist')
        orders = Order.objects.all().order_by('-date')
        transactions = Transaction.objects.all().order_by('-transaction_date')  # ✅ Fetch from `checkout` app

        # ✅ Debugging log (REMOVE in production)
        print(f"Fetched Data: Artworks({artworks.count()}), Patrons({patrons.count()}), Artists({artists.count()}), Orders({orders.count()}), Transactions({transactions.count()})")

        # ✅ Ensure context variables exist
        context = {
            'artworks': artworks,
            'patrons': patrons,
            'artists': artists,
            'all_orders': orders,
            'transactions': transactions,
        }

        return render(request, 'profiles/admin_dashboard.html', context)

    except PermissionDenied:
        return render(request, 'profiles/403.html', status=403)

    except Exception as e:
        print(f"Unexpected error in admin_dashboard: {e}")  # ✅ Log the actual error
        return render(request, 'profiles/error.html', {'error': str(e)}, status=500)



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
    artworks = Artwork.objects.filter(artist=profile)  # ✅ Fixed Query
    commissions = []  # Replace this if there's a valid commission query

    # Additional stats for the dashboard
    artwork_count = artworks.count()
    commission_count = len(commissions)  # Fix: Ensure commissions exist

    # Prepare the context
    template = 'profiles/artist_profile.html'
    context = {
        'profile': profile,
        'artworks': artworks,
        'artwork_count': artwork_count,
        'commission_count': commission_count,  # Include this in the template
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

    print(f"DEBUG: Loaded Profile for {profile.user.username}")  # ✅ Debug username
    print(f"DEBUG: Profile Data - {profile.__dict__}")  # ✅ Print full profile details

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")  
            return redirect('patron_dashboard')  
        else:
            print(f"DEBUG: Form errors - {form.errors}")  # ✅ Debug Form Errors
            messages.error(request, "Update failed. Please check the form and try again.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profiles/edit_profile.html', {'form': form})





@login_required
def edit_users(request):
    """ Admin edits user roles or details """
    if not request.user.is_superuser:
        raise PermissionDenied("You do not have access to this page.")

    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("role_"):  # Keys like 'role_<user_id>'
                user_id = key.split("_")[1]
                try:
                    user = User.objects.get(id=user_id)
                    if value == 'admin':
                        user.is_staff = True
                        user.is_superuser = True
                    else:
                        user.is_staff = False
                        user.is_superuser = False
                    user.userprofile.role = value  # Update the role in UserProfile
                    user.userprofile.save()
                    user.save()
                except User.DoesNotExist:
                    messages.error(request, f"User with ID {user_id} not found.")
        messages.success(request, "User roles updated successfully!")
        return redirect('edit_users')

    users = User.objects.all()
    return render(request, 'profiles/edit_user.html', {'users': users})


@login_required
def edit_user_detail(request, user_id):
    """ Admin edits specific user details """
    if not request.user.is_superuser:
        raise PermissionDenied("You do not have access to this page.")

    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "User details updated successfully!")
            return redirect('edit_users')

    form = UserProfileForm(instance=profile)
    return render(request, 'profiles/edit_user_detail.html', {'form': form, 'user': user})



@login_required
def delete_user(request, user_id):
    """ Admin deletes a user """
    if not request.user.is_superuser:
        raise PermissionDenied("You do not have access to this page.")

    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('admin_dashboard')


#     # CRUD for Commissions
# def list_commissions(request):
#     """ List all commissions """
#     commissions = Commission.objects.all()
#     return render(request, 'profiles/list_commissions.html', {'commissions': commissions})


# def edit_commission(request, commission_id):
#     """ Edit a commission """
#     commission = get_object_or_404(Commission, id=commission_id)
#     if request.method == "POST":
#         form = CommissionForm(request.POST, instance=commission)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Commission updated successfully!")
#             return redirect('list_commissions')
#     else:
#         form = CommissionForm(instance=commission)
#     return render(request, 'profiles/edit_commission.html', {'form': form})


# def delete_commission(request, commission_id):
#     """ Delete a commission """
#     commission = get_object_or_404(Commission, id=commission_id)
#     commission.delete()
#     messages.success(request, "Commission deleted successfully!")
#     return redirect('list_commissions')


    # CRUD for Transactions
def list_transactions(request):
    """ List all transactions """
    transactions = Transaction.objects.all()
    return render(request, 'profiles/list_transactions.html', {'transactions': transactions})


def edit_transaction(request, transaction_id):
    """ Edit a transaction """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully!")
            return redirect('list_transactions')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'profiles/edit_transaction.html', {'form': form})


def delete_transaction(request, transaction_id):
    """ Delete a transaction """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    messages.success(request, "Transaction deleted successfully!")
    return redirect('list_transactions')


def complete_order(request):
    # Your existing checkout/purchase logic
    order = ...  # Assume the order is created here

    # Get the buyer's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Create a transaction
    Transaction.objects.create(
        user=user_profile,
        amount=order.grand_total,  # Use the order's total amount
        transaction_date=order.created_at  # Or use `timezone.now()` if needed
    )


@login_required
def transaction_detail(request, transaction_id):
    """ View details of a specific transaction """
    transaction = get_object_or_404(Transaction, id=transaction_id)

    return render(request, 'profiles/transaction_detail.html', {
        'transaction': transaction
    })


@login_required
def add_to_wishlist(request, artwork_id):
    """ Add or remove an artwork from the user's wishlist """
    profile = get_object_or_404(UserProfile, user=request.user)
    artwork = get_object_or_404(Artwork, pk=artwork_id)  

    # Debugging: Print to confirm artwork instance
    print(f"Adding/removing artwork: {artwork} (ID: {artwork.id}, Type: {type(artwork)})")

    if profile.wishlist.filter(pk=artwork.pk).exists():
        profile.wishlist.remove(artwork)  
    else:
        profile.wishlist.add(artwork)  

    return redirect('artworks') 


@login_required
def remove_from_wishlist(request, artwork_id):
    """ Remove an artwork from the user's wishlist """
    profile = get_object_or_404(UserProfile, user=request.user)
    artwork = get_object_or_404(Artwork, id=artwork_id)

    if profile.wishlist.filter(pk=artwork.pk).exists():
        profile.wishlist.remove(artwork)  

    return redirect('patron_dashboard') 


@login_required
def wishlist(request):
    """ Display the user's wishlist items """
    profile = get_object_or_404(UserProfile, user=request.user)
    wishlist_items = profile.wishlist.all()

    return render(request, 'profiles/wishlist.html', {'wishlist_items': wishlist_items})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Check if the profile already exists before creating a new one
            profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'user'})
            
            if created:
                messages.success(request, 'Successfully signed up!')
            else:
                messages.warning(request, 'UserProfile already exists. Using existing profile.')

            return redirect('login')  # Adjust redirect as needed
        else:
            messages.error(request, 'Failed to sign up. Please ensure the form is valid.')
    else:
        form = SignupForm()

    return render(request, 'profiles/signup.html', {'form': form})



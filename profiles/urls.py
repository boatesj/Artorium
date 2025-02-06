# profiles/urls.py

from django.urls import path, include
from allauth.account.views import SignupView
from . import views


app_name = 'profiles'

urlpatterns = [
    # Profile & Dashboard Views
    path('', views.profile, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('artist-profile/', views.artist_profile, name='artist_profile'),
    path('patron-dashboard/', views.patron_dashboard, name='patron_dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('signup/', SignupView.as_view(), name='account_signup'),
    path('manage-portfolio/', views.manage_portfolio, name='manage_portfolio'),

    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:artwork_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:artwork_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # User Management
    path('edit-users/', views.edit_users, name='edit_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit-user-detail/<int:user_id>/', views.edit_user_detail, name='edit_user_detail'),

    # Transactions
    path('transactions/', views.list_transactions, name='list_transactions'),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('transaction/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),

    # Order History
    path('order_history/<order_number>/', views.order_history, name='order_history'),
]
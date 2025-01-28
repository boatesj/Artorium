from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('order_history/<order_number>/', views.order_history, name='order_history'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('patron-dashboard/', views.patron_dashboard, name='patron_dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    # path('wishlist/', views.wishlist, name='wishlist'),
    path('edit-users/', views.edit_users, name='edit_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit-user-detail/<int:user_id>/', views.edit_user_detail, name='edit_user_detail'),

]

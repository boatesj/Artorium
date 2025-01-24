from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),  # Loads profile view at /profile/
    path('edit/', views.edit_profile, name='edit_profile'),  # Profile editing
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Admin dashboard
]

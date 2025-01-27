from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('order_history/<order_number>', views.order_history, name='order_history'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('patron-dashboard/', views.patron_dashboard, name='patron_dashboard'),

]
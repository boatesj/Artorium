from django.urls import path
from . import views
from .views import artwork_list

app_name = 'artworks'

urlpatterns = [
    path('', views.gallery_view, name='gallery'),
    path('<int:artwork_id>/', views.artwork_detail_view, name='artwork_detail'),
    path('add/', views.admin_add_artwork_view, name='add_artwork'),
    path('edit/<int:artwork_id>/', views.edit_artwork_view, name='edit_artwork'),
    path('delete/<int:artwork_id>/', views.delete_artwork_view, name='delete_artwork'),
    path('add/artist/', views.artist_add_artwork_view, name='add_artwork_artist'),
    path('manage-portfolio/', views.manage_portfolio, name='manage_portfolio'),
    path('categories/', views.category_list_view, name='category_list'),
    path('', artwork_list, name='artwork_list'), 
]

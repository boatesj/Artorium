from django.urls import path
from . import views

app_name = 'artworks'

urlpatterns = [
    path('', views.all_artworks, name='artworks'), 
    path('<int:artwork_id>/', views.artwork_detail, name='artwork_detail'),
    path('add/', views.add_artwork, name='add_artwork'),
    path('edit/<int:artwork_id>/', views.edit_artwork, name='edit_artwork'),
    path('delete/<int:artwork_id>/', views.delete_artwork, name='delete_artwork'),
    path('add/artist/', views.add_artwork_artist, name='add_artwork_artist'),
    path('manage-portfolio/', views.manage_portfolio, name='manage_portfolio'),
    path('categories/', views.category_list, name='category_list'),
    path('list/', views.artwork_list, name='artwork_list'),  
]

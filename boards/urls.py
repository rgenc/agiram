# boards/urls.py

from django.urls import path
from . import views

app_name = 'boards'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('boards/', views.BoardListView.as_view(), name='board_list'),
    path('boards/new/', views.BoardCreateView.as_view(), name='board_create'),
    path('boards/<int:pk>/', views.BoardDetailView.as_view(), name='board_detail'),
    path('boards/<int:pk>/update/', views.BoardUpdateView.as_view(), name='board_update'),
    path('boards/<int:pk>/delete/', views.BoardDeleteView.as_view(), name='board_delete'),
    path('boards/<int:pk>/add-member/', views.add_board_member, name='add_board_member'),
    path('boards/<int:board_pk>/remove-member/<int:user_pk>/', views.remove_board_member, name='remove_board_member'),
    
    # Liste işlemleri
    path('boards/<int:board_pk>/lists/create/', views.create_list, name='create_list'),
    path('lists/<int:list_pk>/update/', views.update_list, name='update_list'),
    path('lists/<int:list_pk>/delete/', views.delete_list, name='delete_list'),
    path('api/lists/update-position/', views.update_list_position, name='update_list_position'),
    
    # Kart işlemleri
    path('lists/<int:list_pk>/cards/create/', views.create_card, name='create_card'),
    path('cards/<int:card_pk>/', views.card_detail, name='card_detail'),
    path('cards/<int:card_pk>/update/', views.update_card, name='update_card'),
    path('cards/<int:card_pk>/delete/', views.delete_card, name='delete_card'),
    path('cards/<int:card_pk>/assign/', views.assign_card, name='assign_card'),
    path('cards/<int:card_pk>/toggle-complete/', views.toggle_card_complete, name='toggle_card_complete'),
    path('api/cards/update-position/', views.update_card_position, name='update_card_position'),
    
    # Dosya işlemleri
    path('cards/<int:card_pk>/upload-attachment/', views.upload_attachment, name='upload_attachment'),
    path('attachments/<int:attachment_pk>/delete/', views.delete_attachment, name='delete_attachment'),
]
# tours/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('search-results/', views.search_results, name='search_results'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'), # Детальная страница тура
    path('tour/add/', views.tour_add, name='tour_add'),                 # Добавление нового тура
    path('tour/<int:tour_id>/edit/', views.tour_edit, name='tour_edit'), # Редактирование тура
    path('tour/<int:tour_id>/delete/', views.tour_delete, name='tour_delete'), # Удаление тура
]
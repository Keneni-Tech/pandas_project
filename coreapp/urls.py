from django.urls import path
from . import views

urlpatterns = [
    path('', views.chart_view, name='home'), # Example view
    path('list/', views.index_view, name='country'), 
    path('search/', views.search_view, name='search'), 
]

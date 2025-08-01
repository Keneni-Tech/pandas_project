from django.urls import path
from . import views

app_name = "coreapp"

urlpatterns = [
    path('', views.chart_view, name='home'),
    path('list/', views.index_view, name='country'), 
    path('search/', views.search_view, name='search'), 
    path('boxplot/', views.eda_boxplot_view, name='boxplot'),
    path('scatterplot/', views.eda_scatterplot_view, name='scatterplot'),
    path('compare/', views.country_comparison_view, name='compare'),

]

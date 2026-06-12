from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shops/', views.shop_list, name='shop_list'),
    path('shop/<int:pk>/', views.shop_detail, name='shop_detail'),
    path('category/<int:pk>/', views.shop_by_category, name='shop_by_category'),
    path('search/', views.search, name='search'),
    path('shop/<int:pk>/review/', views.add_review, name='add_review'),
    path('analytics/', views.analytics, name='analytics'),
    path('taste/', views.taste_analysis, name='taste_analysis'),
]

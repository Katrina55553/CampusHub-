from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='orders_index'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/accept/', views.accept_order, name='accept_order'),
    path('<int:order_id>/complete/', views.complete_order, name='complete_order'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('search/', views.orders_search, name='orders_search'),
    path('stats/', views.stats, name='orders_stats'),
    path('predict/', views.predict, name='orders_predict'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]

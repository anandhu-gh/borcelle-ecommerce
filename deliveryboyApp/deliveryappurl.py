from .import views
from django.urls import path

urlpatterns = [
    path('home/', views.deliveryHome, name='deliveryhome'),
    path('delivery-orders/', views.deliveryOrders, name='deliveryorders'),
    path('mark-delivered/<int:order_id>/', views.markDelivered, name='markdelivered'),
    path('delivery-history/', views.deliveryHistory, name='deliveryhistory'),
    path('profile/', views.deliveryProfile, name='deleiveryprofile'),
    path('editprofile/', views.editDeliveryProfile, name='editdeliveryprofile'),
  
]
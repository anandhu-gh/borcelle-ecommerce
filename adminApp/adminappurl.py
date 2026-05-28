from .import views
from django.urls import path

urlpatterns = [
    path('adminhome/', views.adminHome, name='adminhome'),
    path('addproductform/', views.addProductForm, name='addproductform'),
    
    path('addproduct/', views.addProduct, name='addproduct'),
    path('addcategory/', views.addCategory, name='addcategory'),
    path('add-location/', views.addLocation, name='addlocation'),
    path('add-delivery-boy/',views.addDeliveryBoy,name='adddeliveryboy'),

    path('adminproducts/', views.productsList, name='adminproducts'),

    path('editproduct/<int:id>/', views.editProduct, name='editproduct'),
    path('deleteproduct/<int:id>/', views.deleteProduct, name='deleteproduct'),

    path('adminorders/', views.orderDetails, name='adminorders'),
    path('adddistrict/', views.LocationRegister, name='adddistrict'),
    path('filllocation', views.fillLocation, name='filllocation'),
    path('filter-products/', views.filter_products, name='filter_products'),

    path('logout/', views.logout, name='logout'),
]

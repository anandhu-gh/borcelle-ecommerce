from .import views
from django.urls import path

urlpatterns = [
    path('profile/', views.customerProfile, name='profile'),
    path('editprofile/', views.editProfile, name='editprofile'),
    path('customerhome/', views.customerHome, name='customerhome'),

    path('productsview/', views.productsList, name='productsview'),
    path('productdetails/<int:id>/<str:name>/', views.productDetails, name='productdetails'),
    path('customer/allcategories/', views.allCategories, name='allcategories'),
    path('customer/category/<int:category_id>/<str:category_name>/', views.categoryView, name='categoryview'),

    path('addtocart/<int:id>/', views.addToCart, name='addtocart'),
    path('removecartitem/<int:id>/', views.removeFromCart, name='removecartitem'),
    path('cart/', views.viewCart, name='cart'),

    path('orderhistory/', views.orderHistory, name='orderhistory'),

    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.paymentPage, name='payment'),
    path('confirmpayment/', views.confirmPayment, name='confirmpayment'),
    path('feedback/<int:id>/', views.submitFeedback, name='submitfeedback'),
]
from . import views
from django.urls import path

urlpatterns = [
    path('', views.homePage, name='home'),
    path('about/', views.aboutPage, name='about'),
    path('terms-policy/', views.termsandpolicyPage, name='termsandpolicy'),
    path('login/', views.loginPage, name='login'),
    path('login_process/', views.loginProcess, name='login_process'),
    path('adminhome/', views.adminHome, name='adminhome'),
    path('guestproducts/', views.productsList, name='guestproducts'),
    path('signup_process/',views.signupProcess,name='signup_process'),
    path('logout/', views.logoutProcess, name='logout'),
]
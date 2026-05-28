from django.db import models


class LoginDetails(models.Model):
    loginId = models.AutoField(primary_key = True)
    username = models.CharField(max_length = 25)
    password = models.CharField(max_length = 15)
    role = models.CharField(max_length = 25)
    status = models.CharField(max_length = 25)

class Customer(models.Model):
    loginId = models.ForeignKey('LoginDetails', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    district = models.ForeignKey('adminApp.District',on_delete=models.CASCADE,null=True,blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    location = models.TextField(max_length=500, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
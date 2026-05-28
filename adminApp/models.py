from django.db import models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50)
    category_image = models.ImageField(upload_to='category_image/', null=True, blank=True)


class Product(models.Model):
    ProductId = models.AutoField(primary_key=True)
    ProductName = models.CharField(max_length=200)
    ProductDescription = models.TextField()
    ProductImage = models.ImageField(upload_to='products/', null=True, blank=True)
    ProductPrice = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')


class District(models.Model):
    district_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    district_id = models.ForeignKey('District', on_delete=models.CASCADE)
    location = models.CharField(max_length=200)

class DeliveryBoy(models.Model):
    loginId = models.ForeignKey('guestApp.LoginDetails', on_delete=models.CASCADE)

    deliveryboy_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    email = models.EmailField()

    username = models.CharField(max_length=100)

    password = models.CharField(max_length=100)


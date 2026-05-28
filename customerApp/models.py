from django.db import models


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)

    customer = models.ForeignKey('guestApp.Customer', on_delete=models.CASCADE)
    product = models.ForeignKey('adminApp.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
   
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)

    customer = models.ForeignKey('guestApp.Customer', on_delete=models.CASCADE)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=50, default="Pending")

class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)  # explicit id

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey('adminApp.Product', on_delete=models.CASCADE)

    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)

    customer = models.ForeignKey('guestApp.Customer', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    card_last4 = models.CharField(max_length=4)

    status = models.CharField(max_length=20, default="Paid")
    created_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)

    customer = models.ForeignKey('guestApp.Customer', on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('adminApp.Product', on_delete=models.CASCADE)

    rating = models.IntegerField()
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
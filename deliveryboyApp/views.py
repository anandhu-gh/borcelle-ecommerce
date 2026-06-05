from django.shortcuts import render, redirect
from django.http import HttpResponse

from guestApp.models import LoginDetails, Customer
from adminApp.models import District, Product, Category, DeliveryBoy
from customerApp.models import Cart, Order, OrderItem, Payment

def deliveryHome(request):

    paid_orders = Order.objects.filter(payment__status="Paid")

    total_orders = paid_orders.count()

    pending_orders = paid_orders.filter(status="Pending").count()

    delivered_orders = paid_orders.filter(status="Delivered").count()

    return render(request, 'deliveryboy/deliveryHome.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders
    })

def deliveryOrders(request):

    paid_orders = Order.objects.filter(payment__status="Paid").distinct().order_by('-order_id')

    return render(request, 'deliveryboy/orders.html', {
        'paid_orders': paid_orders
    })

def markDelivered(request, order_id):
    order = Order.objects.filter(order_id=order_id).first()
    if order:
        order.status = "Delivered"
        order.save()
    return redirect('deliveryorders')

def deliveryHistory(request):
    orders = Order.objects.filter(status="Delivered", payment__status="Paid").distinct()

    return render(request, "deliveryboy/orderHistory.html", {"orders": orders})

def deliveryProfile(request):

    login_id = request.session['loginId']

    deliveryboy = DeliveryBoy.objects.get(loginId=login_id)

    return render(request, 'deliveryboy/profile.html', {
        'deliveryboy': deliveryboy
    })

def editDeliveryProfile(request):

    login_id = request.session['loginId']

    deliveryboy = DeliveryBoy.objects.get(loginId=login_id)
    login_data = LoginDetails.objects.get(loginId=login_id)

    if request.method == "POST":

        username = request.POST.get('username')
        new_password = request.POST.get('new_password')

        # username already exists
        if LoginDetails.objects.filter(username=username).exclude(loginId=login_id).exists():
            return HttpResponse("<script>alert('Username already exists!');window.location='/delivery/editprofile/'</script>")


        # update details
        deliveryboy.name = request.POST.get('name')
        deliveryboy.phone = request.POST.get('phone')
        deliveryboy.address = request.POST.get('address')
        deliveryboy.email = request.POST.get('email')
        deliveryboy.username = username

        login_data.username = username

        # update password only if entered
        if new_password != "":

            deliveryboy.password = new_password
            login_data.password = new_password

        deliveryboy.save()
        login_data.save()

        return HttpResponse(
            "<script>alert('Profile updated successfully');window.location='/delivery/profile/'</script>"
        )

    return render(request, 'deliveryboy/editProfile.html', {
        'deliveryboy': deliveryboy
    })
from django.shortcuts import render, redirect
from django.http import HttpResponse

from guestApp.models import LoginDetails, Customer
from adminApp.models import District, Product, Category, DeliveryBoy
from customerApp.models import Cart, Order, OrderItem, Payment


# ---------------------------------------------------
# DELIVERY BOY DASHBOARD (HOME PAGE)
# ---------------------------------------------------
def deliveryHome(request):
    # only count orders where the payment was actually completed ("Paid")
    paid_orders = Order.objects.filter(payment__status="Paid")

    total_orders = paid_orders.count()
    pending_orders = paid_orders.filter(status="Pending").count()
    delivered_orders = paid_orders.filter(status="Delivered").count()

    return render(request, 'deliveryboy/deliveryHome.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders
    })


# ---------------------------------------------------
# LIST OF ALL PAID ORDERS (for delivery boy to act on)
# ---------------------------------------------------
def deliveryOrders(request):
    # distinct() avoids duplicate rows if an order has multiple related rows
    paid_orders = Order.objects.filter(payment__status="Paid").distinct().order_by('-order_id')

    return render(request, 'deliveryboy/orders.html', {
        'paid_orders': paid_orders
    })


# ---------------------------------------------------
# MARK AN ORDER AS DELIVERED
# ---------------------------------------------------
def markDelivered(request, order_id):
    # find the order, or None if it doesn't exist
    order = Order.objects.filter(order_id=order_id).first()

    if order:
        order.status = "Delivered"
        order.save()

    # go back to the orders list page (url name: "deliveryorders")
    return redirect('deliveryorders')


# ---------------------------------------------------
# SHOW DELIVERY HISTORY (only delivered + paid orders)
# ---------------------------------------------------
def deliveryHistory(request):
    orders = Order.objects.filter(status="Delivered", payment__status="Paid").distinct()

    return render(request, "deliveryboy/orderHistory.html", {"orders": orders})


# ---------------------------------------------------
# SHOW DELIVERY BOY'S OWN PROFILE
# ---------------------------------------------------
def deliveryProfile(request):
    # get the logged-in delivery boy's login id from session
    login_id = request.session['loginId']

    deliveryboy = DeliveryBoy.objects.get(loginId=login_id)

    return render(request, 'deliveryboy/profile.html', {
        'deliveryboy': deliveryboy
    })


# ---------------------------------------------------
# EDIT DELIVERY BOY'S PROFILE
# ---------------------------------------------------
def editDeliveryProfile(request):
    login_id = request.session['loginId']

    deliveryboy = DeliveryBoy.objects.get(loginId=login_id)
    login_data = LoginDetails.objects.get(loginId=login_id)

    if request.method == "POST":
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')

        # check the new username isn't already taken by someone else
        if LoginDetails.objects.filter(username=username).exclude(loginId=login_id).exists():
            return HttpResponse("<script>alert('Username already exists!');window.location='/delivery/editprofile/'</script>")

        # update the basic details
        deliveryboy.name = request.POST.get('name')
        deliveryboy.phone = request.POST.get('phone')
        deliveryboy.address = request.POST.get('address')
        deliveryboy.email = request.POST.get('email')
        deliveryboy.username = username

        login_data.username = username

        # only update the password if a new one was actually typed in
        if new_password != "":
            deliveryboy.password = new_password
            login_data.password = new_password

        deliveryboy.save()
        login_data.save()

        return HttpResponse(
            "<script>alert('Profile updated successfully');window.location='/delivery/profile/'</script>"
        )

    # GET request: show the form with current details filled in
    return render(request, 'deliveryboy/editProfile.html', {
        'deliveryboy': deliveryboy
    })
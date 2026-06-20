from django.shortcuts import render, redirect
from django.http import HttpResponse

from guestApp.models import LoginDetails, Customer
from adminApp.models import District, Product, Category, DeliveryBoy
from customerApp.models import Cart, Order, OrderItem, Payment


# delivery boy dashboard / home page
def deliveryHome(request):
    # only counting orders where the payment is actually "Paid"
    paid_orders = Order.objects.filter(payment__status="Paid")

    total_orders = paid_orders.count()
    pending_orders = paid_orders.filter(status="Pending").count()
    delivered_orders = paid_orders.filter(status="Delivered").count()

    return render(request, 'deliveryboy/deliveryHome.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders
    })


# list of all paid orders for the delivery boy
def deliveryOrders(request):
    # distinct() so we dont get duplicate rows if order has multiple related rows
    paid_orders = Order.objects.filter(payment__status="Paid").distinct().order_by('-order_id')

    return render(request, 'deliveryboy/orders.html', {
        'paid_orders': paid_orders
    })


# marks an order as delivered
def markDelivered(request, order_id):
    # get the order, or None if it doesnt exist
    order = Order.objects.filter(order_id=order_id).first()

    if order:
        order.status = "Delivered"
        order.save()

    # go back to the orders list page (url name "deliveryorders")
    return redirect('deliveryorders')


# shows delivery history (only delivered and paid orders)
def deliveryHistory(request):
    orders = Order.objects.filter(status="Delivered", payment__status="Paid").distinct()

    return render(request, "deliveryboy/orderHistory.html", {"orders": orders})


# shows delivery boy's own profile
def deliveryProfile(request):
    # getting logged in delivery boy's login id from session
    login_id = request.session['loginId']

    deliveryboy = DeliveryBoy.objects.get(loginId=login_id)

    return render(request, 'deliveryboy/profile.html', {
        'deliveryboy': deliveryboy
    })


# edit delivery boy's profile
def editDeliveryProfile(request):
    login_id = request.session['loginId']

    deliveryboy = DeliveryBoy.objects.get(loginId=login_id)
    login_data = LoginDetails.objects.get(loginId=login_id)

    if request.method == "POST":
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')

        # check new username isnt taken by someone else already
        if LoginDetails.objects.filter(username=username).exclude(loginId=login_id).exists():
            return HttpResponse("<script>alert('Username already exists!');window.location='/delivery/editprofile/'</script>")

        # updating the basic details
        deliveryboy.name = request.POST.get('name')
        deliveryboy.phone = request.POST.get('phone')
        deliveryboy.address = request.POST.get('address')
        deliveryboy.email = request.POST.get('email')
        deliveryboy.username = username

        login_data.username = username

        # only update password if a new one was actually entered
        if new_password != "":
            deliveryboy.password = new_password
            login_data.password = new_password

        deliveryboy.save()
        login_data.save()

        return HttpResponse(
            "<script>alert('Profile updated successfully');window.location='/delivery/profile/'</script>"
        )

    # GET request - show form filled with current details
    return render(request, 'deliveryboy/editProfile.html', {
        'deliveryboy': deliveryboy
    })
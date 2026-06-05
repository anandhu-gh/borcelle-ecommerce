from django.shortcuts import render, redirect
from django.http import HttpResponse



from guestApp.models import LoginDetails, Customer
from adminApp.models import District, Product, Category
from customerApp.models import Cart, Order, OrderItem, Payment, Feedback

def customerHome(request):
    return render(request, 'Customer/customerHome.html')

def aboutPage(request):
    return render(request, 'Customer/about.html')

def termsandpolicyPage(request):
    return render(request, 'Customer/terms.html')

def customerProfile(request):
    login_id = request.session.get('loginId')

    customer_details = Customer.objects.get(loginId_id=login_id)

    return render(request, 'Customer/customerProfile.html', {
        'customer_details': customer_details
    })

def productsList(request):
    product_details = Product.objects.all()
    return render(request, 'Customer/productView.html', {'product_details': product_details,'action': 'list'})

def productDetails(request, id,name):
    product = Product.objects.get(ProductId = id)
    reviews = Feedback.objects.filter(product=product)

    if request.method == "POST":
        p_name = request.POST.get('name')
        p_description = request.POST.get('description')
        p_image = request.FILES.get('image')
        p_price = request.POST.get('price')
        product.save()

    return render(request, 'Customer/productDetails.html', {
        'product': product,
        'reviews': reviews
    })

def allCategories(request):
    categories = Category.objects.prefetch_related('products').all()
    return render(request, 'Customer/allCategories.html', {'categories': categories})

def categoryView(request, category_id, category_name=None):
    # Fetch category by ID
    category = Category.objects.get(category_id=category_id)
    
    # products that belong to this category
    products = Product.objects.filter(category=category)
    
    return render(request, 'Customer/categoryView.html', {
        'category': category,
        'products': products
    })

def addToCart(request, id):
    if request.method == "POST":

        login_id = request.session.get('loginId')

        if not login_id:
            return HttpResponse("<script>alert('Please login first');window.location='/login'</script>")

        try:
            customer = Customer.objects.get(loginId_id=login_id)
            product = Product.objects.get(ProductId=id)

            qty = int(request.POST.get('quantity', 1))

            # check if already exists
            cart_item = Cart.objects.filter(customer=customer, product=product).first()

            if cart_item:
                cart_item.quantity += qty
                cart_item.save()
            else:
                Cart.objects.create(
                    customer=customer,
                    product=product,
                    quantity=qty
                )

            return HttpResponse("<script>alert('Added to Cart');window.location='/customer/cart/'</script>")

        except:
            return HttpResponse("<script>alert('Error occurred');window.location='/'</script>")
        
def removeFromCart(request, id):

    cart_item = Cart.objects.get(cart_id=id)
    cart_item.delete()

    return redirect('cart')  # your cart page name

def viewCart(request):
    # 1. Get login id from session
    login_id = request.session.get('loginId')

    # 2. If user not logged in → go to login page
    if not login_id:
        return redirect('login')

    # 3. Get current customer using login id
    customer = Customer.objects.get(loginId_id=login_id)

    # 4. Get all cart items for this customer
    cart_items = Cart.objects.filter(customer=customer)

    

    total = 0
    for item in cart_items:
        item.item_total = item.product.ProductPrice * item.quantity
        total += item.item_total

    return render(request, 'Customer/cart.html', {'cart_items': cart_items,'total': total})

def orderHistory(request):
    # 1. Get the current user's ID from the session
    login_id = request.session.get('loginId')
    
    # 2. Redirect to login if they aren't logged in
    if not login_id:
        return redirect('login')

    # 3. Find the Customer record linked to this login
    user = Customer.objects.get(loginId_id=login_id)

    # 4. Get all orders for this customer (newest at the top)
    # We use '-order_id' to show the most recent order first
    my_orders = Order.objects.filter(customer=user).order_by('-order_id')

    # 5. Send 'my_orders' to the HTML page
    return render(request, 'Customer/orderHistory.html', {'orders': my_orders, 'user' : user})

def checkout(request):
    login_id = request.session.get('loginId')

    if not login_id:
        return redirect('login')

    customer = Customer.objects.get(loginId_id=login_id)

    cart_items = Cart.objects.filter(customer=customer)

    total = 0
    for item in cart_items:
        item.item_total = item.product.ProductPrice * item.quantity
        total += item.item_total

    return render(request, 'Customer/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'customer': customer
    })

def paymentPage(request):
    login_id = request.session.get('loginId')

    if not login_id:
        return redirect('login')

    customer = Customer.objects.get(loginId_id=login_id)
    cart_items = Cart.objects.filter(customer=customer)

    total = sum(item.product.ProductPrice * item.quantity for item in cart_items)

    # 🔥 lock checkout session (important fix)
    request.session['checkout_started'] = True

    return render(request, 'Customer/payment.html', {
        'total': total,
        'cart_items': cart_items
    })

def confirmPayment(request):

    if request.method != "POST":
        return redirect('cart')

    login_id = request.session.get('loginId')
    if not login_id:
        return redirect('login')

    # 🔥 prevent multiple orders per checkout
    if not request.session.get('checkout_started'):
        return HttpResponse("<script>alert('Invalid checkout session');window.location='/cart'</script>")

    customer = Customer.objects.get(loginId_id=login_id)
    cart_items = Cart.objects.filter(customer=customer)

    if not cart_items:
        return redirect('cart')

    total = sum(item.product.ProductPrice * item.quantity for item in cart_items)

    card_number = request.POST.get('card_number')
    last4 = card_number[-4:] if card_number else "0000"

    # ✔ ONE ORDER ONLY HERE
    order = Order.objects.create(
        customer=customer,
        total_amount=total
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.ProductPrice
        )
        item.product.stock -= item.quantity
        item.product.save()

    Payment.objects.create(
        customer=customer,
        order=order,
        amount=total,
        card_last4=last4,
    )

    cart_items.delete()

    # 🔥 close checkout session
    request.session['checkout_started'] = False

    return HttpResponse(
        f"<script>alert('Order #{order.order_id} placed successfully');window.location='/customer/orderhistory/'</script>"
    )

def editProfile(request):

    login_id = request.session.get('loginId')

    customer = Customer.objects.get(loginId_id=login_id)
    login = customer.loginId

    if request.method == "POST":

        customer.phone = request.POST.get('phone')
        customer.email = request.POST.get('email')
        customer.location = request.POST.get('location')
        customer.address = request.POST.get('address')
        customer.pincode = request.POST.get('pincode')

        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        dist_id = request.POST.get('district')

        if dist_id:
            customer.district = District.objects.get(district_id=dist_id)

        # FIXED duplicate check
        if LoginDetails.objects.filter(username=new_username).exclude(loginId=login_id).exists():
            return HttpResponse("<script>alert('Username already exists');window.location='/customer/editprofile/'</script>")
        login.username = new_username

        # password update
        if new_password:
            login.password = new_password
            customer.password = new_password

        login.save()

        customer.username = new_username
        customer.save()

        return HttpResponse("<script>alert('Profile updated successfully');window.location='/customer/profile/'</script>")

    districts = District.objects.all()

    return render(request, 'Customer/editProfile.html', {
        'customer_details': customer,
        'districts': districts
    })

def submitFeedback(request, id):

    login_id = request.session.get('loginId')

    if request.method == "POST":

        customer = Customer.objects.get(loginId_id=login_id)
        order = Order.objects.get(order_id=id)

        saved = 0  # count how many feedbacks are saved

        for item in order.orderitem_set.all():

            rating = request.POST.get(f"rating_{item.order_item_id}")
            message = request.POST.get(f"message_{item.order_item_id}", "").strip()

            if rating or message:
                Feedback.objects.create(
                    customer=customer,
                    order=order,
                    product=item.product,
                    rating=int(rating) if rating else 5,
                    message=message
                )
                saved += 1

        # ❌ if nothing was saved
        if saved == 0:
            return HttpResponse("""
                <script>
                    alert('Please enter at least one feedback');
                    window.history.back();
                </script>
            """)

        # ✅ success
        return HttpResponse("""
            <script>
                alert('Feedback submitted successfully');
                window.location='/customer/orderhistory/';
            </script>
        """)

    return redirect('orderhistory')


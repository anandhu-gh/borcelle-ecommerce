from django.shortcuts import render, redirect
from django.http import HttpResponse

from guestApp.models import LoginDetails, Customer
from adminApp.models import District, Product, Category
from customerApp.models import Cart, Order, OrderItem, Payment, Feedback


# customer home page
def customerHome(request):
    return render(request, 'Customer/customerHome.html')


# about page
def aboutPage(request):
    return render(request, 'Customer/about.html')


# terms and policy page
def termsandpolicyPage(request):
    return render(request, 'Customer/terms.html')


# shows the logged in customer's own profile
def customerProfile(request):
    # getting the logged in user id from session
    login_id = request.session.get('loginId')

    # finding their customer details using that login id
    customer_details = Customer.objects.get(loginId_id=login_id)

    return render(request, 'Customer/customerProfile.html', {
        'customer_details': customer_details
    })


# shows all products on customer side
def productsList(request):
    product_details = Product.objects.all()
    return render(request, 'Customer/productView.html', {
        'product_details': product_details,
        'action': 'list'
    })


# shows one product's details along with its reviews
def productDetails(request, id, name):
    product = Product.objects.get(ProductId=id)

    # getting all the feedback/reviews for this product
    reviews = Feedback.objects.filter(product=product)

    # this part normally a customer shouldnt edit product from here,
    # but keeping it as it was, just fixed it so it actually updates
    # the product properly instead of saving nothing
    if request.method == "POST":
        p_name = request.POST.get('name')
        p_description = request.POST.get('description')
        p_image = request.FILES.get('image')
        p_price = request.POST.get('price')

        product.ProductName = p_name
        product.ProductDescription = p_description
        product.ProductPrice = p_price

        if p_image:
            product.ProductImage = p_image

        product.save()

    return render(request, 'Customer/productDetails.html', {
        'product': product,
        'reviews': reviews
    })


# shows all categories with their products loaded already
def allCategories(request):
    # prefetch_related makes it faster, loads all products in one go
    # instead of one query for each category one by one
    categories = Category.objects.prefetch_related('products').all()
    return render(request, 'Customer/allCategories.html', {'categories': categories})


# shows products that belong to one category
def categoryView(request, category_id, category_name=None):
    # find the category using its id
    category = Category.objects.get(category_id=category_id)

    # get all products under this category
    products = Product.objects.filter(category=category)

    return render(request, 'Customer/categoryView.html', {
        'category': category,
        'products': products
    })


# adds a product into the cart
def addToCart(request, id):
    if request.method == "POST":
        login_id = request.session.get('loginId')

        # has to be logged in first
        if not login_id:
            return HttpResponse("<script>alert('Please login first');window.location='/login'</script>")

        try:
            customer = Customer.objects.get(loginId_id=login_id)
            product = Product.objects.get(ProductId=id)

            # how many to add, default is 1 if not given
            qty = int(request.POST.get('quantity', 1))

            # check if this product is already added in cart before
            cart_item = Cart.objects.filter(customer=customer, product=product).first()

            if cart_item:
                # already there, so just increase the quantity
                cart_item.quantity += qty
                cart_item.save()
            else:
                # not there yet, so add a new cart row
                Cart.objects.create(
                    customer=customer,
                    product=product,
                    quantity=qty
                )

            return HttpResponse("<script>alert('Added to Cart');window.location='/customer/cart/'</script>")

        except Exception:
            # something went wrong somewhere (maybe product not found etc)
            return HttpResponse("<script>alert('Error occurred');window.location='/'</script>")


# removes one item from the cart
def removeFromCart(request, id):
    cart_item = Cart.objects.get(cart_id=id)
    cart_item.delete()

    return redirect('cart')  # back to cart page


# shows the cart with total price
def viewCart(request):
    # 1. getting logged in user id
    login_id = request.session.get('loginId')

    # 2. not logged in, send to login
    if not login_id:
        return redirect('login')

    # 3. get the customer linked to this login
    customer = Customer.objects.get(loginId_id=login_id)

    # 4. get all cart items of this customer
    cart_items = Cart.objects.filter(customer=customer)

    # 5. calculate price for each item, and the grand total
    total = 0
    for item in cart_items:
        item.item_total = item.product.ProductPrice * item.quantity
        total += item.item_total

    return render(request, 'Customer/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# shows the customer's past orders
def orderHistory(request):
    # 1. get login id from session
    login_id = request.session.get('loginId')

    # 2. not logged in, send to login page
    if not login_id:
        return redirect('login')

    # 3. find the customer for this login
    user = Customer.objects.get(loginId_id=login_id)

    # 4. get all their orders, newest first
    my_orders = Order.objects.filter(customer=user).order_by('-order_id')

    # 5. send to template
    return render(request, 'Customer/orderHistory.html', {
        'orders': my_orders,
        'user': user
    })


# shows the checkout page (cart summary before paying)
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


# shows the payment page
def paymentPage(request):
    login_id = request.session.get('loginId')

    if not login_id:
        return redirect('login')

    customer = Customer.objects.get(loginId_id=login_id)
    cart_items = Cart.objects.filter(customer=customer)

    # adding up the total price of cart
    total = sum(item.product.ProductPrice * item.quantity for item in cart_items)

    # marking that checkout has started, so confirmPayment knows
    # this is a real checkout and not someone randomly posting
    request.session['checkout_started'] = True

    return render(request, 'Customer/payment.html', {
        'total': total,
        'cart_items': cart_items
    })


# confirms payment - this is where the order actually gets created
def confirmPayment(request):

    # this should only be reached by submitting the form
    if request.method != "POST":
        return redirect('cart')

    login_id = request.session.get('loginId')
    if not login_id:
        return redirect('login')

    # making sure customer actually went through paymentPage first
    # this stops duplicate orders from happening
    if not request.session.get('checkout_started'):
        return HttpResponse("<script>alert('Invalid checkout session');window.location='/cart'</script>")

    customer = Customer.objects.get(loginId_id=login_id)
    cart_items = Cart.objects.filter(customer=customer)

    # nothing in cart, go back
    if not cart_items:
        return redirect('cart')

    total = sum(item.product.ProductPrice * item.quantity for item in cart_items)

    # just taking last 4 digits of card number to show later
    card_number = request.POST.get('card_number')
    last4 = card_number[-4:] if card_number else "0000"

    # creating just ONE order for the whole cart
    order = Order.objects.create(
        customer=customer,
        total_amount=total
    )

    # creating order items one by one, and reducing stock too
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.ProductPrice
        )
        item.product.stock -= item.quantity
        item.product.save()

    # creating the payment record for this order
    Payment.objects.create(
        customer=customer,
        order=order,
        amount=total,
        card_last4=last4,
    )

    # emptying the cart now since order is placed
    cart_items.delete()

    # closing the checkout session so it cant be reused again
    request.session['checkout_started'] = False

    return HttpResponse(
        f"<script>alert('Order #{order.order_id} placed successfully');window.location='/customer/orderhistory/'</script>"
    )


# edit customer profile
def editProfile(request):
    login_id = request.session.get('loginId')

    customer = Customer.objects.get(loginId_id=login_id)
    login = customer.loginId  # related login account

    if request.method == "POST":
        # updating basic details
        customer.phone = request.POST.get('phone')
        customer.email = request.POST.get('email')
        customer.location = request.POST.get('location')
        customer.address = request.POST.get('address')
        customer.pincode = request.POST.get('pincode')

        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        dist_id = request.POST.get('district')

        # update district if one was selected
        if dist_id:
            customer.district = District.objects.get(district_id=dist_id)

        # checking new username isnt already used by someone else
        if LoginDetails.objects.filter(username=new_username).exclude(loginId=login_id).exists():
            return HttpResponse("<script>alert('Username already exists');window.location='/customer/editprofile/'</script>")

        login.username = new_username

        # only change password if a new one was actually typed
        if new_password:
            login.password = new_password
            customer.password = new_password

        login.save()

        customer.username = new_username
        customer.save()

        return HttpResponse("<script>alert('Profile updated successfully');window.location='/customer/profile/'</script>")

    # GET request - show the edit form with current details filled in
    districts = District.objects.all()

    return render(request, 'Customer/editProfile.html', {
        'customer_details': customer,
        'districts': districts
    })


# submitting feedback for items in an order
def submitFeedback(request, id):
    login_id = request.session.get('loginId')

    if request.method == "POST":
        customer = Customer.objects.get(loginId_id=login_id)
        order = Order.objects.get(order_id=id)

        saved = 0  # counting how many feedbacks we actually saved

        # going through every item in this order
        for item in order.orderitem_set.all():

            # form sends rating and message per item using the item id
            rating = request.POST.get(f"rating_{item.order_item_id}")
            message = request.POST.get(f"message_{item.order_item_id}", "").strip()

            # only save if customer actually wrote something
            if rating or message:
                Feedback.objects.create(
                    customer=customer,
                    order=order,
                    product=item.product,
                    rating=int(rating) if rating else 5,
                    message=message
                )
                saved += 1

        # nothing got filled in at all
        if saved == 0:
            return HttpResponse("""
                <script>
                    alert('Please enter at least one feedback');
                    window.history.back();
                </script>
            """)

        return HttpResponse("""
            <script>
                alert('Feedback submitted successfully');
                window.location='/customer/orderhistory/';
            </script>
        """)

    # GET request - just go back to order history
    return redirect('orderhistory')
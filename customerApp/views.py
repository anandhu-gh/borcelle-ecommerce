from django.shortcuts import render, redirect
from django.http import HttpResponse

from guestApp.models import LoginDetails, Customer
from adminApp.models import District, Product, Category
from customerApp.models import Cart, Order, OrderItem, Payment, Feedback


# ---------------------------------------------------
# CUSTOMER HOME PAGE
# ---------------------------------------------------
def customerHome(request):
    return render(request, 'Customer/customerHome.html')


# ---------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------
def aboutPage(request):
    return render(request, 'Customer/about.html')


# ---------------------------------------------------
# TERMS AND POLICY PAGE
# ---------------------------------------------------
def termsandpolicyPage(request):
    return render(request, 'Customer/terms.html')


# ---------------------------------------------------
# SHOW LOGGED-IN CUSTOMER'S PROFILE
# ---------------------------------------------------
def customerProfile(request):
    # get the logged-in user's id from the session
    login_id = request.session.get('loginId')

    # find their customer profile using that login id
    customer_details = Customer.objects.get(loginId_id=login_id)

    return render(request, 'Customer/customerProfile.html', {
        'customer_details': customer_details
    })


# ---------------------------------------------------
# SHOW LIST OF ALL PRODUCTS (customer-facing)
# ---------------------------------------------------
def productsList(request):
    product_details = Product.objects.all()
    return render(request, 'Customer/productView.html', {
        'product_details': product_details,
        'action': 'list'
    })


# ---------------------------------------------------
# SHOW DETAILS OF ONE PRODUCT + ITS REVIEWS
# ---------------------------------------------------
def productDetails(request, id, name):
    product = Product.objects.get(ProductId=id)

    # get all feedback/reviews left for this product
    reviews = Feedback.objects.filter(product=product)

    # NOTE: a normal customer should not be able to edit a product
    # from this page. This POST block is left here in case it's used
    # for something else, but it now actually updates the product
    # correctly instead of saving empty changes.
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


# ---------------------------------------------------
# SHOW ALL CATEGORIES (with their products preloaded)
# ---------------------------------------------------
def allCategories(request):
    # prefetch_related makes this faster by loading all related
    # products in one go, instead of one query per category
    categories = Category.objects.prefetch_related('products').all()
    return render(request, 'Customer/allCategories.html', {'categories': categories})


# ---------------------------------------------------
# SHOW PRODUCTS BELONGING TO ONE CATEGORY
# ---------------------------------------------------
def categoryView(request, category_id, category_name=None):
    # find the category using its id
    category = Category.objects.get(category_id=category_id)

    # get all products that belong to this category
    products = Product.objects.filter(category=category)

    return render(request, 'Customer/categoryView.html', {
        'category': category,
        'products': products
    })


# ---------------------------------------------------
# ADD A PRODUCT TO THE CART
# ---------------------------------------------------
def addToCart(request, id):
    if request.method == "POST":
        login_id = request.session.get('loginId')

        # must be logged in to add to cart
        if not login_id:
            return HttpResponse("<script>alert('Please login first');window.location='/login'</script>")

        try:
            customer = Customer.objects.get(loginId_id=login_id)
            product = Product.objects.get(ProductId=id)

            # how many of this product to add (default 1)
            qty = int(request.POST.get('quantity', 1))

            # check if this product is already in the cart
            cart_item = Cart.objects.filter(customer=customer, product=product).first()

            if cart_item:
                # already in cart, just increase the quantity
                cart_item.quantity += qty
                cart_item.save()
            else:
                # not in cart yet, create a new cart entry
                Cart.objects.create(
                    customer=customer,
                    product=product,
                    quantity=qty
                )

            return HttpResponse("<script>alert('Added to Cart');window.location='/customer/cart/'</script>")

        except Exception:
            # something went wrong (e.g. product not found)
            return HttpResponse("<script>alert('Error occurred');window.location='/'</script>")


# ---------------------------------------------------
# REMOVE AN ITEM FROM THE CART
# ---------------------------------------------------
def removeFromCart(request, id):
    cart_item = Cart.objects.get(cart_id=id)
    cart_item.delete()

    return redirect('cart')  # goes back to the cart page


# ---------------------------------------------------
# VIEW THE CART (with totals)
# ---------------------------------------------------
def viewCart(request):
    # 1. get logged-in user's id
    login_id = request.session.get('loginId')

    # 2. not logged in? send to login page
    if not login_id:
        return redirect('login')

    # 3. get the customer for this login
    customer = Customer.objects.get(loginId_id=login_id)

    # 4. get all cart items belonging to this customer
    cart_items = Cart.objects.filter(customer=customer)

    # 5. work out the price for each item, and the grand total
    total = 0
    for item in cart_items:
        item.item_total = item.product.ProductPrice * item.quantity
        total += item.item_total

    return render(request, 'Customer/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# ---------------------------------------------------
# SHOW THE CUSTOMER'S PAST ORDERS
# ---------------------------------------------------
def orderHistory(request):
    # 1. get logged-in user's id from session
    login_id = request.session.get('loginId')

    # 2. not logged in? send to login page
    if not login_id:
        return redirect('login')

    # 3. find the customer linked to this login
    user = Customer.objects.get(loginId_id=login_id)

    # 4. get all their orders, newest first
    my_orders = Order.objects.filter(customer=user).order_by('-order_id')

    # 5. send to the template
    return render(request, 'Customer/orderHistory.html', {
        'orders': my_orders,
        'user': user
    })


# ---------------------------------------------------
# SHOW CHECKOUT PAGE (cart summary before payment)
# ---------------------------------------------------
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


# ---------------------------------------------------
# SHOW PAYMENT PAGE
# ---------------------------------------------------
def paymentPage(request):
    login_id = request.session.get('loginId')

    if not login_id:
        return redirect('login')

    customer = Customer.objects.get(loginId_id=login_id)
    cart_items = Cart.objects.filter(customer=customer)

    # add up total price of everything in the cart
    total = sum(item.product.ProductPrice * item.quantity for item in cart_items)

    # mark that checkout has started, so confirmPayment() knows
    # this is a real checkout and not a random direct POST
    request.session['checkout_started'] = True

    return render(request, 'Customer/payment.html', {
        'total': total,
        'cart_items': cart_items
    })


# ---------------------------------------------------
# CONFIRM PAYMENT (creates the order + payment, empties cart)
# ---------------------------------------------------
def confirmPayment(request):

    # this page should only be reached through a form POST
    if request.method != "POST":
        return redirect('cart')

    login_id = request.session.get('loginId')
    if not login_id:
        return redirect('login')

    # make sure the customer actually went through paymentPage() first
    # (this stops someone from placing duplicate orders)
    if not request.session.get('checkout_started'):
        return HttpResponse("<script>alert('Invalid checkout session');window.location='/cart'</script>")

    customer = Customer.objects.get(loginId_id=login_id)
    cart_items = Cart.objects.filter(customer=customer)

    # nothing in the cart? go back
    if not cart_items:
        return redirect('cart')

    total = sum(item.product.ProductPrice * item.quantity for item in cart_items)

    # just grab last 4 digits of the "card number" for display purposes
    card_number = request.POST.get('card_number')
    last4 = card_number[-4:] if card_number else "0000"

    # create ONE order for this whole cart
    order = Order.objects.create(
        customer=customer,
        total_amount=total
    )

    # create one OrderItem per cart item, and reduce stock
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.ProductPrice
        )
        item.product.stock -= item.quantity
        item.product.save()

    # create the payment record for this order
    Payment.objects.create(
        customer=customer,
        order=order,
        amount=total,
        card_last4=last4,
    )

    # empty the cart now that the order is placed
    cart_items.delete()

    # close the checkout session so it can't be reused
    request.session['checkout_started'] = False

    return HttpResponse(
        f"<script>alert('Order #{order.order_id} placed successfully');window.location='/customer/orderhistory/'</script>"
    )


# ---------------------------------------------------
# EDIT CUSTOMER PROFILE
# ---------------------------------------------------
def editProfile(request):
    login_id = request.session.get('loginId')

    customer = Customer.objects.get(loginId_id=login_id)
    login = customer.loginId  # the related login account

    if request.method == "POST":
        # update basic info
        customer.phone = request.POST.get('phone')
        customer.email = request.POST.get('email')
        customer.location = request.POST.get('location')
        customer.address = request.POST.get('address')
        customer.pincode = request.POST.get('pincode')

        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        dist_id = request.POST.get('district')

        # update district if one was chosen
        if dist_id:
            customer.district = District.objects.get(district_id=dist_id)

        # check that the new username isn't already used by someone else
        if LoginDetails.objects.filter(username=new_username).exclude(loginId=login_id).exists():
            return HttpResponse("<script>alert('Username already exists');window.location='/customer/editprofile/'</script>")

        login.username = new_username

        # only change password if a new one was typed in
        if new_password:
            login.password = new_password
            customer.password = new_password

        login.save()

        customer.username = new_username
        customer.save()

        return HttpResponse("<script>alert('Profile updated successfully');window.location='/customer/profile/'</script>")

    # GET request: show the edit form with current details
    districts = District.objects.all()

    return render(request, 'Customer/editProfile.html', {
        'customer_details': customer,
        'districts': districts
    })


# ---------------------------------------------------
# SUBMIT FEEDBACK FOR ITEMS IN AN ORDER
# ---------------------------------------------------
def submitFeedback(request, id):
    login_id = request.session.get('loginId')

    if request.method == "POST":
        customer = Customer.objects.get(loginId_id=login_id)
        order = Order.objects.get(order_id=id)

        saved = 0  # count how many feedbacks we actually saved

        # go through every item in this order
        for item in order.orderitem_set.all():

            # the form sends rating/message per item, using the item's id
            rating = request.POST.get(f"rating_{item.order_item_id}")
            message = request.POST.get(f"message_{item.order_item_id}", "").strip()

            # only save feedback if the customer actually entered something
            if rating or message:
                Feedback.objects.create(
                    customer=customer,
                    order=order,
                    product=item.product,
                    rating=int(rating) if rating else 5,
                    message=message
                )
                saved += 1

        # nothing was filled in at all
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

    # GET request: just go back to order history
    return redirect('orderhistory')
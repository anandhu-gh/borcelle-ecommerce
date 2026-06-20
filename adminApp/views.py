from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

# Importing models from other apps that we need to use here
from adminApp.models import Category, Product, District, Location, DeliveryBoy
from customerApp.models import Order, OrderItem, Payment
from guestApp.models import LoginDetails


# ---------------------------------------------------
# ADMIN DASHBOARD (HOME PAGE)
# ---------------------------------------------------
def adminHome(request):
    # count how many products and categories we have
    total_products = Product.objects.count()
    total_categories = Category.objects.count()

    # get all payments that are "Paid", newest first
    payments = Payment.objects.filter(status="Paid").order_by('-created_at')

    # add up all the paid payments to get total revenue
    total_revenue = 0
    for pay in payments:
        total_revenue += pay.amount

    # send all this info to the admin home page
    return render(request, 'Admin/index.html', {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_revenue': total_revenue
    })


# ---------------------------------------------------
# SHOW THE "ADD PRODUCT" FORM (empty form, GET request)
# ---------------------------------------------------
def addProductForm(request):
    # we need the list of categories to show in a dropdown
    categories = Category.objects.all()

    return render(request, 'Admin/addProduct.html', {'categories': categories})


# ---------------------------------------------------
# ADD A NEW CATEGORY
# ---------------------------------------------------
def addCategory(request):
    if request.method == "POST":
        # get the data sent from the form
        name = request.POST.get('category_name')
        image = request.FILES.get('category_image')

        # check if this category name is already used (case-insensitive)
        if Category.objects.filter(category_name__iexact=name).exists():
            return HttpResponse("""
                <script>
                    alert('Category already exists!');
                    window.location.href = '/admin/addcategory/';
                </script>
            """)

        # if not, create a new category
        Category.objects.create(
            category_name=name,
            category_image=image
        )

        return HttpResponse("""
            <script>
                alert('Category added successfully!');
                window.location.href = '/admin/addcategory/';
            </script>
        """)

    # if it's just a normal page visit (GET), show the empty form
    return render(request, 'Admin/addCategory.html')


# ---------------------------------------------------
# ADD A NEW PRODUCT
# ---------------------------------------------------
def addProduct(request):
    # get list of categories for the dropdown
    categories = Category.objects.all()

    if request.method == 'POST':
        # get all the values from the form
        p_name = request.POST.get('name')
        p_description = request.POST.get('description')
        p_image = request.FILES.get('image')
        p_price = request.POST.get('price')
        p_stock = request.POST.get('stock')
        cat_id = request.POST.get('category')

        # check if a product with this name already exists
        if Product.objects.filter(ProductName__iexact=p_name).exists():
            return HttpResponse("""
                <script>
                    alert('Product already exists!!');
                    window.location='/addproduct';
                </script>
            """)

        # find the category object using the id from the form
        category_obj = Category.objects.get(category_id=cat_id)

        # create the product (not saved yet)
        product = Product(
            ProductName=p_name,
            ProductDescription=p_description,
            ProductImage=p_image,
            ProductPrice=p_price,
            category=category_obj,
            stock=p_stock
        )

        # now actually save it to the database
        product.save()

        return HttpResponse("""
            <script>
                alert('Product added successfully!!');
                window.location='/admin/addproductform/';
            </script>
        """)

    # if GET request, just show the empty add-product form
    return render(request, 'Admin/addProduct.html', {
        'categories': categories
    })


# ---------------------------------------------------
# ADD A NEW LOCATION (under a district)
# ---------------------------------------------------
def addLocation(request):
    # get all districts to show in dropdown
    districts = District.objects.all()

    if request.method == "POST":
        district_id = request.POST.get('district')
        location = request.POST.get('location')

        # find the district object using the id
        district = District.objects.get(district_id=district_id)

        # check if this location already exists (case-insensitive)
        if Location.objects.filter(location__iexact=location).exists():
            return HttpResponse("""
                <script>
                    alert('Location already exists!!');
                    window.location='/admin/add-location/';
                </script>
            """)

        # create the new location
        Location.objects.create(
            district_id=district,
            location=location
        )

        # redirect back to the same page (using the url name "addlocation")
        return redirect('addlocation')

    return render(request, 'Admin/registerLocation.html', {
        'districts': districts
    })


# ---------------------------------------------------
# ADD A NEW DELIVERY BOY (and create a login for them)
# ---------------------------------------------------
def addDeliveryBoy(request):
    if request.method == "POST":
        # get form values
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # check if the username is already taken
        if LoginDetails.objects.filter(username=username).exists():
            return HttpResponse(
                "<script>alert('Username already exists');window.location='/admin/add-delivery-boy/'</script>"
            )

        # first create a login account for this delivery boy
        login = LoginDetails.objects.create(
            username=username,
            password=password,
            role='DeliveryBoy'
        )
        login.save()

        # then create the delivery boy profile, linked to that login
        DeliveryBoy.objects.create(
            loginId=login,
            name=name,
            phone=phone,
            address=address,
            email=email,
            username=username,
            password=password
        )

        return HttpResponse(
            "<script>alert('Delivery person added successfully');window.location='/admin/add-delivery-boy/'</script>"
        )

    # GET request: show the form, plus a list of existing delivery boys
    delivery_boys = DeliveryBoy.objects.all()

    context = {
        'delivery_boys': delivery_boys
    }
    return render(request, 'Admin/addDeliveryBoy.html', context)


# ---------------------------------------------------
# DELETE A DELIVERY BOY (and their login too)
# ---------------------------------------------------
def deleteDeliveryBoy(request, id):
    # find the delivery boy using the id from the url
    deliveryboy = DeliveryBoy.objects.get(deliveryboy_id=id)

    # deleting their login also removes the delivery boy
    # (because delivery boy is linked to login)
    deliveryboy.loginId.delete()

    return HttpResponse(
        "<script>alert('Delivery Boy deleted sucessfully!!');window.location='/admin/add-delivery-boy/'</script>"
    )


# ---------------------------------------------------
# SHOW LIST OF ALL PRODUCTS (admin product list page)
# ---------------------------------------------------
def productsList(request):
    categories = Category.objects.all()
    product_details = Product.objects.all()

    return render(request, 'Admin/products.html', {
        'product_details': product_details,
        'action': 'list',
        'categories': categories
    })


# ---------------------------------------------------
# SHOW DETAILS OF ONE PRODUCT
# ---------------------------------------------------
def productDetails(request, id):
    # find the product using the id from the url
    product = Product.objects.get(ProductId=id)

    if request.method == "POST":
        # get the new values from the form
        p_name = request.POST.get('name')
        p_description = request.POST.get('description')
        p_image = request.FILES.get('image')
        p_price = request.POST.get('price')

        # IMPORTANT: we have to actually put the new values onto
        # the product before saving, otherwise saving does nothing!
        product.ProductName = p_name
        product.ProductDescription = p_description
        product.ProductPrice = p_price

        # only change the image if a new one was uploaded
        if p_image:
            product.ProductImage = p_image

        product.save()

    return render(request, 'Admin/productDetails.html', {'product': product, 'action': 'list'})


# ---------------------------------------------------
# EDIT AN EXISTING PRODUCT
# ---------------------------------------------------
def editProduct(request, id):
    product = Product.objects.get(ProductId=id)
    categories = Category.objects.all()
    duplicate = False  # this will become True if the new name is already used by another product

    if request.method == 'POST':
        new_name = request.POST.get('name')

        # check if another product (not this one) already has this name
        if Product.objects.filter(ProductName__iexact=new_name).exclude(ProductId=id).exists():
            duplicate = True
        else:
            # safe to update the basic fields
            product.ProductName = new_name
            product.ProductDescription = request.POST.get('description')
            product.ProductPrice = request.POST.get('price')
            product.stock = request.POST.get('stock')

        # get category and image OUTSIDE the if/else above,
        # so these lines always run (this fixes a bug where
        # "new_image" was sometimes undefined)
        new_image = request.FILES.get('image')
        cat_id = request.POST.get('category')

        if cat_id:
            product.category = Category.objects.get(category_id=cat_id)

        if new_image:
            product.ProductImage = new_image

        # only save if there was no duplicate name problem
        if not duplicate:
            product.save()
            return HttpResponse(
                """<script>alert('Product updated successfully!');window.location.href='/admin/adminproducts/';</script>"""
            )

    # GET request, or POST with a duplicate name problem: show the form again
    return render(request, 'Admin/editProduct.html', {
        'product': product,
        'action': 'list',
        'duplicate': duplicate,
        'categories': categories
    })


# ---------------------------------------------------
# DELETE A PRODUCT
# ---------------------------------------------------
def deleteProduct(request, id):
    Product.objects.filter(ProductId=id).delete()
    return HttpResponse(
        "<script>alert('Product deleted sucessfully!!');window.location='/admin/adminproducts/'</script>"
    )


# ---------------------------------------------------
# SHOW ALL ORDERS (with optional date filter)
# ---------------------------------------------------
def orderDetails(request):

    # 1. Get all paid payments (default, before any filtering)
    payments = Payment.objects.filter(status="Paid").order_by('-created_at')

    # 2. Get the dates from the filter form, if the admin submitted one
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    # 3. If both dates were given, filter payments to that date range
    if start_date and end_date:
        payments = payments.filter(created_at__date__range=[start_date, end_date])

    # 4. Build up the list of orders with extra info attached
    orders = []
    total_revenue = 0

    for payment in payments:
        order = payment.order  # get the order linked to this payment

        # get all the items that belong to this order
        items = OrderItem.objects.filter(order=order)

        # attach extra info onto the order object so the template can use it
        order.items = items
        order.payment = payment

        # add up the revenue
        total_revenue += payment.amount

        orders.append(order)

    # 5. Send everything to the template
    return render(request, 'Admin/orders.html', {
        'orders': orders,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date
    })


# ---------------------------------------------------
# SHOW THE LOCATION REGISTER PAGE
# ---------------------------------------------------
def LocationRegister(request):
    districts = District.objects.all()
    return render(request, 'admin/locationRegister.html', {'districts': districts})


# ---------------------------------------------------
# AJAX: GET ALL LOCATIONS FOR A GIVEN DISTRICT
# (used to fill a dropdown without reloading the page)
# ---------------------------------------------------
def fillLocation(request):
    did = request.POST.get('did')  # district id sent from the ajax call

    # get all locations belonging to this district, as plain dictionaries
    locations = Location.objects.filter(district_id=did).values()

    # send back as JSON so javascript can use it
    return JsonResponse(list(locations), safe=False)


# ---------------------------------------------------
# AJAX: FILTER PRODUCTS BY CATEGORY
# (used on a page where you click a category and products update
#  without reloading the page)
# ---------------------------------------------------
def filter_products(request):
    category = request.GET.get('category')

    if category == "all":
        products = Product.objects.all()
    else:
        products = Product.objects.filter(category_id=category)

    # build a simple list of dictionaries (easy to convert to JSON)
    data = []
    for p in products:
        data.append({
            'id': p.ProductId,
            'name': p.ProductName,
            'price': str(p.ProductPrice),
            'stock': p.stock,
            'image': p.ProductImage.url
        })

    return JsonResponse(data, safe=False)


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
def logout(request):
    # clear everything stored in the session (like loginId)
    request.session.flush()

    return redirect('login')
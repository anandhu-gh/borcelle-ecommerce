from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

# importing models from other apps so i can use them here
from adminApp.models import Category, Product, District, Location, DeliveryBoy
from customerApp.models import Order, OrderItem, Payment
from guestApp.models import LoginDetails


# admin dashboard home page
def adminHome(request):
    # counting total products and categories for the dashboard
    total_products = Product.objects.count()
    total_categories = Category.objects.count()

    # getting only the paid payments, newest one first
    payments = Payment.objects.filter(status="Paid").order_by('-created_at')

    # now adding up all the paid amounts to get total revenue
    total_revenue = 0
    for pay in payments:
        total_revenue += pay.amount

    # sending everything to the admin home template
    return render(request, 'Admin/index.html', {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_revenue': total_revenue
    })


# just shows the empty add product form (when admin opens the page first time)
def addProductForm(request):
    # need categories to fill the dropdown in the form
    categories = Category.objects.all()

    return render(request, 'Admin/addProduct.html', {'categories': categories})


# adding a new category
def addCategory(request):
    if request.method == "POST":
        # taking the values from the form
        name = request.POST.get('category_name')
        image = request.FILES.get('category_image')

        # checking if category already exists (ignoring upper/lower case)
        if Category.objects.filter(category_name__iexact=name).exists():
            return HttpResponse("""
                <script>
                    alert('Category already exists!');
                    window.location.href = '/admin/addcategory/';
                </script>
            """)

        # if no duplicate, go ahead and create it
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

    # this runs when admin just opens the page (GET request)
    return render(request, 'Admin/addCategory.html')


# adding a new product
def addProduct(request):
    # categories needed for the dropdown
    categories = Category.objects.all()

    if request.method == 'POST':
        # getting all form values one by one
        p_name = request.POST.get('name')
        p_description = request.POST.get('description')
        p_image = request.FILES.get('image')
        p_price = request.POST.get('price')
        p_stock = request.POST.get('stock')
        cat_id = request.POST.get('category')

        # checking if same product name already exists
        if Product.objects.filter(ProductName__iexact=p_name).exists():
            return HttpResponse("""
                <script>
                    alert('Product already exists!!');
                    window.location='/addproduct';
                </script>
            """)

        # getting the category object using the id we got from form
        category_obj = Category.objects.get(category_id=cat_id)

        # making the product object (not saved in db yet)
        product = Product(
            ProductName=p_name,
            ProductDescription=p_description,
            ProductImage=p_image,
            ProductPrice=p_price,
            category=category_obj,
            stock=p_stock
        )

        # now saving it for real
        product.save()

        return HttpResponse("""
            <script>
                alert('Product added successfully!!');
                window.location='/admin/addproductform/';
            </script>
        """)

    # show the blank form again
    return render(request, 'Admin/addProduct.html', {
        'categories': categories
    })


def addLocation(request):
    districts = District.objects.all()

    if request.method == "POST":
        district_id = request.POST.get('district')
        location_name = request.POST.get('location', '').strip()

        if district_id and location_name:
            # Match duplicates against underlying foreign key column format
            exists = Location.objects.filter(district_id_id=district_id, location__iexact=location_name).exists()
            
            if exists:
                return HttpResponse("<script>alert('Location already exists!'); window.history.back();</script>")
            
            # Save the new row
            Location.objects.create(district_id_id=district_id, location=location_name)
            
            # Direct historical referrer back-reload ensures popup renders completely 
            return HttpResponse("<script>alert('Location added successfully!!'); window.location.replace(document.referrer);</script>")

    return render(request, 'Admin/locationRegister.html', {'districts': districts})


def filter_locations(request):
    district_id = request.GET.get('district')

    if district_id == "all" or not district_id:
        locations = Location.objects.all()
    else:
        locations = Location.objects.filter(district_id_id=district_id)

    data = [{'location': loc.location} for loc in locations]
    return JsonResponse(data, safe=False)


# adding a new delivery boy, this also makes a login for them
def addDeliveryBoy(request):
    if request.method == "POST":
        # getting all the values from form
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # check if username already taken
        if LoginDetails.objects.filter(username=username).exists():
            return HttpResponse(
                "<script>alert('Username already exists');window.location='/admin/add-delivery-boy/'</script>"
            )

        # first make the login for this delivery boy
        login = LoginDetails.objects.create(
            username=username,
            password=password,
            role='DeliveryBoy'
        )
        login.save()

        # now make the actual delivery boy and link it to the login above
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

    # GET request - show the form along with existing delivery boys list
    delivery_boys = DeliveryBoy.objects.all()

    context = {
        'delivery_boys': delivery_boys
    }
    return render(request, 'Admin/addDeliveryBoy.html', context)


# deleting a delivery boy (and their login too)
def deleteDeliveryBoy(request, id):
    # getting the delivery boy using id from url
    deliveryboy = DeliveryBoy.objects.get(deliveryboy_id=id)

    # deleting the login automatically deletes the delivery boy too
    # since they are connected
    deliveryboy.loginId.delete()

    return HttpResponse(
        "<script>alert('Delivery Boy deleted sucessfully!!');window.location='/admin/add-delivery-boy/'</script>"
    )


# shows the list of all products in admin side
def productsList(request):
    categories = Category.objects.all()
    product_details = Product.objects.all()

    return render(request, 'Admin/products.html', {
        'product_details': product_details,
        'action': 'list',
        'categories': categories
    })


# shows details for one single product
def productDetails(request, id):
    # find the product using id from url
    product = Product.objects.get(ProductId=id)

    if request.method == "POST":
        # taking new values from the form
        p_name = request.POST.get('name')
        p_description = request.POST.get('description')
        p_image = request.FILES.get('image')
        p_price = request.POST.get('price')

        # need to actually set these on the product first
        # otherwise saving wont change anything
        product.ProductName = p_name
        product.ProductDescription = p_description
        product.ProductPrice = p_price

        # only update image if a new one was actually uploaded
        if p_image:
            product.ProductImage = p_image

        product.save()

    return render(request, 'Admin/productDetails.html', {'product': product, 'action': 'list'})


# editing an existing product
def editProduct(request, id):
    product = Product.objects.get(ProductId=id)
    categories = Category.objects.all()
    duplicate = False  # this turns true if some other product already has this name

    if request.method == 'POST':
        new_name = request.POST.get('name')

        # checking if another product (not this one) is already using this name
        if Product.objects.filter(ProductName__iexact=new_name).exclude(ProductId=id).exists():
            duplicate = True
        else:
            # no duplicate, so update the normal fields
            product.ProductName = new_name
            product.ProductDescription = request.POST.get('description')
            product.ProductPrice = request.POST.get('price')
            product.stock = request.POST.get('stock')

        # keeping these two outside the if/else above
        # so they always run no matter what (fixes a bug
        # where new_image was not defined sometimes)
        new_image = request.FILES.get('image')
        cat_id = request.POST.get('category')

        if cat_id:
            product.category = Category.objects.get(category_id=cat_id)

        if new_image:
            product.ProductImage = new_image

        # save only if there was no duplicate name issue
        if not duplicate:
            product.save()
            return HttpResponse(
                """<script>alert('Product updated successfully!');window.location.href='/admin/adminproducts/';</script>"""
            )

    # either GET request, or POST with duplicate name - show form again
    return render(request, 'Admin/editProduct.html', {
        'product': product,
        'action': 'list',
        'duplicate': duplicate,
        'categories': categories
    })


# deleting a product
def deleteProduct(request, id):
    Product.objects.filter(ProductId=id).delete()
    return HttpResponse(
        "<script>alert('Product deleted sucessfully!!');window.location='/admin/adminproducts/'</script>"
    )


# shows all orders, can filter by date too
def orderDetails(request):

    # step 1: get all paid payments first (default, no filter applied yet)
    payments = Payment.objects.filter(status="Paid").order_by('-created_at')

    # step 2: check if admin submitted any start/end date in the filter form
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    # step 3: if both dates are given, filter the payments using that range
    if start_date and end_date:
        payments = payments.filter(created_at__date__range=[start_date, end_date])

    # step 4: now build the orders list with some extra info attached
    orders = []
    total_revenue = 0

    for payment in payments:
        order = payment.order  # the order linked to this payment

        # get all order items belonging to this order
        items = OrderItem.objects.filter(order=order)

        # attaching extra stuff to the order object so template can use it directly
        order.items = items
        order.payment = payment

        # keep adding to total revenue
        total_revenue += payment.amount

        orders.append(order)

    # step 5: finally send everything to the template
    return render(request, 'Admin/orders.html', {
        'orders': orders,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date
    })





# ajax call - gets all locations for the district picked
# (used so the location dropdown updates without reloading page)
def fillLocation(request):
    did = request.POST.get('did')  # district id coming from the ajax request

    # getting all locations under this district, as plain dicts
    locations = Location.objects.filter(district_id=did).values()

    # sending back as json so js can use it on the other side
    return JsonResponse(list(locations), safe=False)


# ajax call - filters products by category
# (used on the page where products change when you pick a category,
# without refreshing the whole page)
def filter_products(request):
    category = request.GET.get('category')

    if category == "all":
        products = Product.objects.all()
    else:
        products = Product.objects.filter(category_id=category)

    # making a simple list of dicts so it can be turned into json easily
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


# logs the user out
def logout(request):
    # this clears everything in session, like loginId
    request.session.flush()

    return redirect('login')
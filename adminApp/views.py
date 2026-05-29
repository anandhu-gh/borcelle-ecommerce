from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from adminApp.models import Category, Product, District, Location, DeliveryBoy
from customerApp.models import Order,OrderItem,Payment
from guestApp.models import LoginDetails

def adminHome(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()

    payments = Payment.objects.filter(status="Paid").order_by('-created_at')

    total_revenue = 0

    # Loop through each payment

    for pay in payments:
        # add payment amount to total revenue
        total_revenue += pay.amount


    return render(request, 'Admin/index.html', {'total_products' : total_products, 
            'total_categories' : total_categories, 'total_revenue': total_revenue})

def addProductForm(request):
    categories = Category.objects.all()

    return render(request, 'Admin/addProduct.html', {'categories': categories})

def addCategory(request):
    if request.method == "POST":
        name = request.POST.get('category_name')
        image = request.FILES.get('category_image')

        if Category.objects.filter(category_name__iexact=name).exists():
            return HttpResponse("""
                <script>
                    alert('Category already exists!');
                    window.location.href = '/admin/addcategory/';
                </script>
            """)

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

    return render(request, 'Admin/addCategory.html')

def addProduct(request):

    categories = Category.objects.all()

    if request.method == 'POST':
        p_name = request.POST.get('name')
        p_description = request.POST.get('description')
        p_image = request.FILES.get('image')
        p_price = request.POST.get('price')
        p_stock = request.POST.get('stock')
        cat_id = request.POST.get('category')

        if Product.objects.filter(ProductName__iexact=p_name).exists():
            return HttpResponse("""
                <script>
                    alert('Product already exists!!');
                    window.location='/addproduct';
                </script>
            """)

        category_obj = Category.objects.get(category_id=cat_id)

        product = Product(
            ProductName=p_name,
            ProductDescription=p_description,
            ProductImage=p_image,
            ProductPrice=p_price,
            category=category_obj,
            stock=p_stock 
        )

        product.save()

        return HttpResponse("""
            <script>
                alert('Product added successfully!!');
                window.location='/admin/addproductform/';
            </script>
        """)

    return render(request, 'Admin/addProduct.html', {
        'categories': categories
    })

def addLocation(request):

    districts = District.objects.all()

    if request.method == "POST":

        district_id = request.POST.get('district')
        location = request.POST.get('location')

        district = District.objects.get(district_id=district_id)

        if Location.objects.filter(location__iexact=location).exists():
            return HttpResponse("""
                <script>
                    alert('Location already exists!!');
                    window.location='/admin/add-location/';
                </script>
            """)
        Location.objects.create(
            district_id=district,
            location=location
        )

        return redirect('addlocation')

    return render(request, 'Admin/registerLocation.html', {
        'districts': districts
    })

def addDeliveryBoy(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if username exists
        if LoginDetails.objects.filter(username=username).exists():
            return HttpResponse("<script>alert('Username already exists');window.location='/admin/add-delivery-boy/'</script>")

        # Create login
        login = LoginDetails.objects.create(
            username=username,
            password=password,
            role='DeliveryBoy'
        )
        login.save()

        # Create delivery boy
        DeliveryBoy.objects.create(
            loginId=login,
            name=name,
            phone=phone,
            address=address,
            email=email,
            username=username,
            password=password
        )

        return HttpResponse("<script>alert('Delivery person added successfully');window.location='/admin/add-delivery-boy/'</script>")

    # Fetch all delivery boys to display them on the page
    delivery_boys = DeliveryBoy.objects.all()
    
    context = {
        'delivery_boys': delivery_boys
    }
    return render(request, 'Admin/addDeliveryBoy.html', context)

def productsList(request):
    categories = Category.objects.all()
    product_details = Product.objects.all()
    return render(request, 'Admin/products.html', {'product_details': product_details,'action': 'list', 'categories' : categories})



def productDetails(request,id):
    product = Product.objects.get(ProductId = id)

    if request.method == "POST":
        p_name = request.POST.get('name')
        p_description = request.POST.get('description')
        p_image = request.FILES.get('image')
        p_price = request.POST.get('price')
        product.save()
    
    return render(request, 'Admin/productDetails.html', {'product': product, 'action': 'list'})

def editProduct(request, id):
    product = Product.objects.get(ProductId=id)
    categories = Category.objects.all()
    duplicate = False

    if request.method == 'POST':
        new_name = request.POST.get('name')

        if Product.objects.filter(ProductName__iexact=new_name).exclude(ProductId=id).exists():
            duplicate = True
        else:
            product.ProductName = new_name
            product.ProductDescription = request.POST.get('description')
            product.ProductPrice = request.POST.get('price')
            product.stock = request.POST.get('stock')

            new_image = request.FILES.get('image')

        cat_id = request.POST.get('category')
        
        if cat_id:
            product.category = Category.objects.get(category_id=cat_id)

        if new_image:
            product.ProductImage = new_image

        product.save()

        return HttpResponse("""<script>alert('Product updated successfully!');window.location.href='/admin/adminproducts/';</script>""")

    return render(request, 'Admin/editProduct.html', {
        'product': product,
        'action': 'list',
        'duplicate': duplicate,
        'categories' : categories
    })
    return redirect('Admin/products.html')

def deleteProduct(request, id):
    Product.objects.filter(ProductId=id).delete()
    return HttpResponse("<script>alert('Product deleted sucessfully!!');window.location='/admin/adminproducts/'</script>")



def orderDetails(request):

    # 1. Get all paid payments (default)
    payments = Payment.objects.filter(status="Paid").order_by('-created_at')

    # 2. Get dates from form (if submitted)
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    # 3. If both dates exist → filter payments
    if start_date and end_date:
        payments = payments.filter(created_at__date__range=[start_date, end_date])

    # 4. Prepare data
    orders = []
    total_revenue = 0

    for payment in payments:

        order = payment.order   # get order

        # get all products of this order
        items = OrderItem.objects.filter(order=order)

        # attach extra data to order
        order.items = items
        order.payment = payment

        # add revenue
        total_revenue += payment.amount

        # add to list
        orders.append(order)

    # 5. Send to HTML
    return render(request, 'Admin/orders.html', {
        'orders': orders,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date
    })

def LocationRegister(request):
    districts = District.objects.all()
    return render(request, 'admin/locationRegister.html', {'districts': districts})


def fillLocation(request):
    did = request.POST.get('did')

    locations = Location.objects.filter(district_id=did).values()

    return JsonResponse(list(locations), safe=False)

def filter_products(request):
    category = request.GET.get('category')

    if category == "all":
        products = Product.objects.all()
    else:
        products = Product.objects.filter(category_id=category)

    data = list(products.values(
        'ProductId',
        'ProductName',
        'ProductDescription',
        'ProductPrice',
        'stock',
        'ProductImage'
    ))

    return JsonResponse(data, safe=False)

def logout(request):

    request.session.flush()

    return redirect('login')
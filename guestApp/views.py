from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import LoginDetails, Customer
from adminApp.models import District, Product


# home page for visitors who havent logged in yet
def homePage(request):
    return render(request, 'Guest/home.html')


# about page
def aboutPage(request):
    return render(request, 'Guest/about.html')


# terms and policy page
def termsandpolicyPage(request):
    return render(request, 'Guest/terms.html')


# shows product list before login (guest side)
def productsList(request):
    product_details = Product.objects.all()
    return render(request, 'Guest/products.html', {
        'product_details': product_details,
        'action': 'list'
    })


# shows the login / signup page
def loginPage(request):
    # needed for the district dropdown in signup form
    dist = District.objects.all()
    return render(request, 'Guest/loginRegister.html', {'dist': dist})


# admin home (kept as it was, even though adminApp already has its own one)
def adminHome(request):
    return render(request, 'Admin/index.html')


# handles login form submit
def loginProcess(request):
    if request.method == "POST":
        name = request.POST.get('username')
        password = request.POST.get('password')

        # check if username + password matches something in db
        if LoginDetails.objects.filter(username=name, password=password).exists():
            logindata = LoginDetails.objects.get(username=name, password=password)

            # storing logged in user id in session
            request.session['loginId'] = logindata.loginId
            role = logindata.role

            if role == 'Admin':
                return HttpResponse(
                    "<script>alert('Welcome to Admin Panel');window.location='/admin/adminhome/'</script>"
                )

            elif role == 'customer':
                return HttpResponse(
                    "<script>alert('Welcome Back!');window.location='/customer/home/'</script>"
                )

            elif role == 'DeliveryBoy':
                return HttpResponse(
                    "<script>alert('Logged in as Delivery person');window.location='/delivery/home/'</script>"
                )

            else:
                # safety net, just in case role doesnt match any of the above
                # without this django would complain that view returned nothing
                return HttpResponse(
                    "<script>alert('Unknown user role');window.location='/login'</script>"
                )

        else:
            # username/password didnt match anything in db
            return HttpResponse(
                "<script>alert('Invalid Username or Password');window.location='/login'</script>"
            )

    # GET request, not a form submit, just go to login page
    return redirect('login')


# handles signup form submit, creates a new customer account
def signupProcess(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        dist_id = request.POST.get('district')
        location = request.POST.get('location')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # check username isnt already taken
        if LoginDetails.objects.filter(username=username).exists():
            return HttpResponse("<script>alert('Username already exists');window.location='/login'</script>")

        # district is required
        if not dist_id:
            return HttpResponse("<script>alert('Select a district');window.location='/login'</script>")

        district = District.objects.get(pk=int(dist_id))

        # step 1, create the login account first
        login = LoginDetails(
            username=username,
            password=password,
            role='customer',
            status='confirmed'
        )
        login.save()

        # log them in right away after signup
        request.session['loginId'] = login.loginId

        # step 2, create the customer profile linked to that login
        customer = Customer(
            loginId=login,
            name=fullname,
            phone=phone,
            email=email,
            district=district,
            location=location,
            address=address,
            pincode=pincode,
            username=username,
            password=password,
        )
        customer.save()

        return HttpResponse("<script>alert('Account Created Successfully');window.location='/customer/home/'</script>")

    # GET request, just send to login/signup page
    return redirect('login')


# logout
def logoutProcess(request):
    # clears the whole session (removes loginId etc)
    request.session.flush()

    return redirect('login')
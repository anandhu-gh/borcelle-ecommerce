from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import LoginDetails, Customer
from adminApp.models import District, Product


# ---------------------------------------------------
# HOME PAGE (for visitors who haven't logged in)
# ---------------------------------------------------
def homePage(request):
    return render(request, 'Guest/home.html')


# ---------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------
def aboutPage(request):
    return render(request, 'Guest/about.html')


# ---------------------------------------------------
# TERMS AND POLICY PAGE
# ---------------------------------------------------
def termsandpolicyPage(request):
    return render(request, 'Guest/terms.html')


# ---------------------------------------------------
# SHOW LIST OF PRODUCTS (guest-facing, before login)
# ---------------------------------------------------
def productsList(request):
    product_details = Product.objects.all()
    return render(request, 'Guest/products.html', {
        'product_details': product_details,
        'action': 'list'
    })


# ---------------------------------------------------
# SHOW LOGIN / SIGNUP PAGE
# ---------------------------------------------------
def loginPage(request):
    # needed for the signup form's district dropdown
    dist = District.objects.all()
    return render(request, 'Guest/loginRegister.html', {'dist': dist})


# ---------------------------------------------------
# ADMIN HOME (kept here as in original, though adminApp
# already has its own adminHome view)
# ---------------------------------------------------
def adminHome(request):
    return render(request, 'Admin/index.html')


# ---------------------------------------------------
# HANDLE LOGIN FORM SUBMISSION
# ---------------------------------------------------
def loginProcess(request):
    if request.method == "POST":
        name = request.POST.get('username')
        password = request.POST.get('password')

        # check if a login with this username + password exists
        if LoginDetails.objects.filter(username=name, password=password).exists():
            logindata = LoginDetails.objects.get(username=name, password=password)

            # store the logged-in user's id in the session
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
                # safety net: role didn't match any known type.
                # Without this, Django would crash because the view
                # would return nothing for this case.
                return HttpResponse(
                    "<script>alert('Unknown user role');window.location='/login'</script>"
                )

        else:
            # username/password didn't match anything
            return HttpResponse(
                "<script>alert('Invalid Username or Password');window.location='/login'</script>"
            )

    # if it's a GET request (not a form submission), just go to login page
    return redirect('login')


# ---------------------------------------------------
# HANDLE SIGNUP FORM SUBMISSION (creates customer account)
# ---------------------------------------------------
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

        # check username isn't already taken
        if LoginDetails.objects.filter(username=username).exists():
            return HttpResponse("<script>alert('Username already exists');window.location='/login'</script>")

        # must choose a district
        if not dist_id:
            return HttpResponse("<script>alert('Select a district');window.location='/login'</script>")

        district = District.objects.get(pk=int(dist_id))

        # step 1: create the login account
        login = LoginDetails(
            username=username,
            password=password,
            role='customer',
            status='confirmed'
        )
        login.save()

        # log them in immediately after signup
        request.session['loginId'] = login.loginId

        # step 2: create the customer profile, linked to that login
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

    # GET request: just send them to the login/signup page
    return redirect('login')


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
def logoutProcess(request):
    # clear the whole session (removes loginId etc.)
    request.session.flush()

    return redirect('login')
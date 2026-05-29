from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import LoginDetails, Customer
from adminApp.models import District, Product


def homePage(request):
    return render(request, 'Guest/home.html')


def productsList(request):
    product_details = Product.objects.all()
    return render(request, 'Guest/products.html', {'product_details': product_details,'action': 'list'})

def loginPage(request):
    dist=District.objects.all()
    return render(request,'Guest/loginRegister.html',{'dist':dist})

def adminHome(request):
    return render(request, 'Admin/index.html')

def loginProcess(request):
    if request.method == "POST":
        name = request.POST.get('username')
        password = request.POST.get('password')

        if LoginDetails.objects.filter(username=name, password=password).exists():
            logindata = LoginDetails.objects.get(username=name, password=password)

            request.session['loginId'] = logindata.loginId
            role = logindata.role

            if role == 'Admin':
                return redirect('adminhome')

            elif role == 'customer':
                return HttpResponse(
                    "<script>alert('Login Successful!');window.location='/customer/home/'</script>"
                )
            elif role == 'DeliveryBoy':
                return HttpResponse(
                    "<script>alert('Logged in as Delivery person');window.location='/delivery/home/'</script>"
                )

        else:
            return HttpResponse(
                "<script>alert('Invalid Username or Password');window.location='/login'</script>"
            )



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

        if LoginDetails.objects.filter(username=username).exists():
            return HttpResponse("<script>alert('Username already exists');window.location='/login'</script>")

        if not dist_id:        
            return HttpResponse("<script>alert('Select a district');window.location='/login'</script>")

        district = District.objects.get(pk=int(dist_id))

        login = LoginDetails(
            username=username,
            password=password,
            role='customer',
            status='confirmed'
        )
        login.save()

        request.session['loginId'] = login.loginId

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

    return redirect('login')

def productsList(request):
    product_details = Product.objects.all()
    return render(request, 'Guest/products.html', {'product_details': product_details,'action': 'list'})

def logoutProcess(request):

    # destroy session
    request.session.flush()

    return redirect('login')







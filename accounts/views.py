import random
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from accounts.forms import LoginForm, SignupForm, RegisterForm
from accounts.models import User, Register


# Create your views here.
def signup_page(request):
    form = SignupForm(request.POST or None)

    if request.user.is_authenticated:
        return redirect('home:home')

    if  request.method != 'POST':
        return render(request, 'accounts/signup_page.html', {'form': form})

    if form.is_valid():
        number   = form.cleaned_data['number']
        username = form.cleaned_data['username']
        email    = form.cleaned_data['email']
        password = form.cleaned_data['password']

        if not form.errors:
            if number is not None:
                request.session['number_register'] = number
                request.session['username']        = username
                request.session['email']           = email
                request.session['password']        = password
                return redirect('accounts:register')
            else:
                form.add_error('number', 'Please enter a valid number')

    return render(request, 'accounts/signup_page.html', {'form': form})

def register_page(request):
    form     = RegisterForm(request.POST or None)
    number   = request.session.get('number_register')

    if request.user.is_authenticated:
        return redirect('home:home')

    if not 'number_register' in request.session or not 'username' in request.session or not 'password' in request.session:
        return redirect('accounts:signup')

    if number is None:
        return redirect('accounts:signup')

    if not Register.objects.filter(phone_number=number).exists():
        code     = str(random.randint(10000, 99999))
        register = Register.objects.create(phone_number=number, code=code)
    else:
        register = Register.objects.get(phone_number=number)

    print(register.code)

    if request.method != 'POST':
        return render(request, 'accounts/signup_page.html', {'form': form})


    if form.is_valid():
        input_code = form.cleaned_data['number_code']
        if not register.is_expired():
            if number != register.phone_number:
                form.add_error('number_code', 'something wrong')

            elif input_code != Register.objects.filter(phone_number=number).order_by("-time").first().code:
                form.add_error('number_code', 'code is wrong')

        else:
            form.add_error('number_code', 'code is expired')
            register.delete()
            code     = str(random.randint(10000, 99999))
            register = Register.objects.create(phone_number=number, code=code)
            print(register.code)

        if not form.errors:
            username    = request.session.get('username')
            email       = request.session.get('email')
            password    = request.session.get('password')
            user        = User.objects.create_user(username=username, number=number, password=password, email=email)
            login(request, user)
            register.delete()
            return redirect('home:home')

    return render(request, 'accounts/signup_page.html', {'form': form})

def login_page(request):
    form = LoginForm(request.POST or None)

    if request.user.is_authenticated:
        return redirect('home:home')

    if  request.method != "POST":
        return render(request, 'accounts/login_page.html', {"form": form})

    if form.is_valid():
        number   = form.cleaned_data.get('number')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        if number:
            if not User.objects.filter(number=number).exists():
                form.add_error('number_or_username', 'Number is not exist')

            if not form.errors:
                user = authenticate(number=number, password=password)

        elif username:
            if not User.objects.filter(username=username).exists():
                form.add_error('number_or_username', "Username not exist")

            if not form.errors:
                number = User.objects.get(username=username).number
                user   = authenticate(number=number, password=password)

        if not form.errors:
            if user is None:
                form.add_error('password', "Its not your password")
                return render(request, 'accounts/login_page.html', {"form": form})
            login(request, user)
            return redirect('home:home')


    return render(request, 'accounts/login_page.html', {"form": form})

def logout_page(request):
    logout(request)
    return redirect('home:home')
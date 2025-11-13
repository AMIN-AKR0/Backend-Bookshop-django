from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from accounts.forms import LoginForm
from accounts.models import User


# Create your views here.
def login_page(request):
    form = LoginForm(request.POST or None)

    if request.user.is_authenticated:
        return redirect('home:home')

    if not request.method == "POST":
        return render(request, 'accounts/login_page.html', {"form": form})

    if form.is_valid():
        email_or_username = form.cleaned_data['email_or_username']
        password = form.cleaned_data['password']

        if form.is_email(email_or_username):
            email = form.clean_email(form.cleaned_data['email_or_username'])
            if not User.objects.filter(email=email).exists():
                form.add_error('email_or_username', 'Email is not exist')
                return render(request, 'accounts/login_page.html', {"form": form})
            user = authenticate(email=email, password=password)
        elif form.is_username(email_or_username):
            username = form.clean_username(form.cleaned_data['email_or_username'])
            if not User.objects.filter(username=username).exists():
                form.add_error('email_or_username', "Username not exist")
                return render(request, 'accounts/login_page.html', {"form": form})
            else:
                email = User.objects.get(username=username).email
                user = authenticate(email=email, password=password)

        if user is None:
            form.add_error('password', "Its not your password")
            return render(request, 'accounts/login_page.html', {"form": form})
        else:
            login(request, user)
            return redirect('home:home')
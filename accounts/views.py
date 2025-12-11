import random
import time
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from accounts.forms import LoginForm, SignupForm1, SignupForm2, RegisterForm, ForgotPasswordForm, ResetPasswordForm, NumberValidation
from accounts.models import User, Register, Author, PhoneResetPassword, EmailResetPassword
from .utils import generate_token, is_valid_uuid, send_email


# Create your views here.
def signup_page(request):
    if request.user.is_authenticated:
        raise Http404

    form = SignupForm1(request.POST or None)

    if 'verify_register' in request.session and request.session['verify_register']:
        if 'verify_number_register' in request.session and 'verify_register_time' in request.session:
            if time.time() - request.session['verify_register_time'] < 600:
                request.session['signup_step'] = 2
                form = SignupForm2(request.POST or None)

                if form.is_valid():
                    number   = request.session.get('verify_number_register')
                    username = form.cleaned_data.get('username')
                    password = form.cleaned_data.get('password')

                    user     = User.objects.create_user(number=number, username=username, password=password)

                    login(request, user)

                    del request.session['verify_number_register']
                    del request.session['verify_register_time']
                    del request.session['signup_step']

                    return redirect('home:home')

                return render(request, 'accounts/signup_page.html', {'form': form})
            else:
                del request.session['verify_number_register']
                del request.session['verify_register_time']
                del request.session['signup_step']

    if form.is_valid():
        number   = form.cleaned_data['number']

        if not form.errors:
            if number is not None:
                request.session['number_register'] = number
                return redirect('accounts:register')
            else:
                form.add_error('number', 'Please enter a valid number')

    return render(request, 'accounts/signup_page.html', {'form': form})

def register_page(request):
    if request.user.is_authenticated:
        raise Http404

    if not 'number_register' in request.session:
        return redirect('accounts:signup')

    form = RegisterForm(request.POST or None)
    number = request.session.get('number_register')

    if not Register.objects.filter(phone_number=number).exists():
        code     = str(random.randint(10000, 99999))
        register = Register.objects.create(phone_number=number, code=code)
    else:
        register = Register.objects.get(phone_number=number)

    # connect to sms panel
    print(register.code)

    if form.is_valid():
        input_code = form.cleaned_data['number_code']
        if not register.is_expired():
            if number != register.phone_number:
                form.add_error('number_code', 'something wrong')

            elif input_code != register.code:
                form.add_error('number_code', 'code is wrong')

        else:
            form.add_error('number_code', 'code is expired')
            register.delete()
            code     = str(random.randint(10000, 99999))
            register = Register.objects.create(phone_number=number, code=code)

            # connect to sms panel
            print(register.code)

        if not form.errors:
            register.delete()
            request.session['verify_number_register'] = number
            request.session['verify_register']        = True
            request.session['verify_register_time']   = time.time()
            return redirect('accounts:signup')

    return render(request, 'accounts/signup_page.html', {'form': form, 'number': number})

def forgot_password_page(request):
    if request.user.is_authenticated:
        raise Http404

    form = ForgotPasswordForm(request.POST or None)

    if form.is_valid():
        email  = form.cleaned_data.get('email')
        number = form.cleaned_data.get('number')

        if number:
            if User.objects.filter(number=number).exists():
                if request.session.get('reset_password_number') and User.objects.filter(number=request.session.get('reset_password_number')).exists():
                    user = User.objects.filter(number=request.session.get('reset_password_number')).first()
                    reset_obj = PhoneResetPassword.objects.filter(user=user).last()

                    if reset_obj and not reset_obj.is_expired():
                        return redirect('accounts:number_validation')

                user = User.objects.get(number=number)
                reset_obj = PhoneResetPassword.objects.filter(user=user).last()

                if not reset_obj or reset_obj.is_expired():
                    code = str(random.randint(10000, 99999))

                    # connect to sms panel
                    print(code)

                    PhoneResetPassword.objects.create(user=user, code=code)

                request.session['reset_password_number'] = number
                return redirect('accounts:number_validation')
            else:
                form.add_error('email_or_number', 'Number not exist')

        elif email:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if not EmailResetPassword.objects.filter(user=user).exists() or EmailResetPassword.objects.filter(user=user).last().is_expired():
                    token = generate_token()
                    EmailResetPassword.objects.create(user=user, token=token)
                    # connect to Email panel
                    print(f"/login/reset-password/{token}")
                    send_email(user.email, 'Bookim', f'For Reset Your Password open link: site_name/user/login/reset-password/{token}')

            else:
                form.add_error('email_or_number', 'Email not exist')

    return render(request, 'accounts/forgot_password.html', {'form': form})

def phone_forgot_password_validation(request):
    if not request.session.get('reset_password_number') or request.user.is_authenticated:
        raise Http404

    user = get_object_or_404(User, number=request.session.get('reset_password_number'))
    obj  = PhoneResetPassword.objects.filter(user=user).last()

    if not obj or obj.is_expired():
        raise Http404

    form = NumberValidation(request.POST or None)

    if form.is_valid():
        code = form.cleaned_data['number_code']

        if not request.session.get('try_reset_password_number'):
            request.session['try_reset_password_number'] = 0

        if request.session.get('try_reset_password_time') and time.time() - request.session.get('try_reset_password_time') > 3600:
            del request.session['try_reset_password_number']
            del request.session['try_reset_password_time']

        if obj.code != code:
            if not request.session.get('try_reset_password_number'):
                request.session['try_reset_password_number'] = 1
            else:
                request.session['try_reset_password_number'] += 1

            form.add_error('number_code', 'code is wrong')

        if obj.is_expired():
            form.add_error('number_code', 'code is expired')

        if request.session.get('try_reset_password_number') > 11:
            request.session['try_reset_password_time'] = time.time()
            form.add_error('number_code', 'too many try')
            return render(request, 'accounts/forgot_password.html', {'form': form})

        if not form.errors:
            request.session['otp_validation'] = True
            request.session['otp_number']     = request.session.get('reset_password_number')
            request.session['otp_time']       = int(time.time())
            del request.session['reset_password_number']

            if request.session.get('try_reset_password_time'):
                del request.session['try_reset_password_time']

            return redirect('accounts:reset_password_by_number', number=request.session.get('otp_number'))

    return render(request, 'accounts/forgot_password.html', {'form': form})

def reset_password_page(request, token=None, number=None):
    if request.user.is_authenticated:
        raise Http404

    if number:

        if not request.session.get('otp_validation') or request.session.get('otp_number') != '0' + str(number):
            raise Http404

        otp_time = request.session.get('otp_time')

        if not otp_time or time.time() - otp_time > 600:
            del request.session['otp_time']
            del request.session['otp_number']
            del request.session['otp_validation']
            raise Http404

        user = get_object_or_404(User, number=request.session.get('otp_number'))

    elif token:
        if not is_valid_uuid(token) or not EmailResetPassword.objects.filter(token=token).exists():
            raise Http404

        obj = EmailResetPassword.objects.filter(token=token).last()

        if not obj or obj.is_expired():
            raise Http404

        user = get_object_or_404(User, id=obj.user.id)

    else:
        raise Http404

    form = ResetPasswordForm(request.POST or None)

    if form.is_valid():
        password = form.cleaned_data.get('password')

        user.set_password(password)
        user.save()

        if request.session.get('otp_validation'):
            del request.session['otp_validation']

        if request.session.get('otp_number'):
            del request.session['otp_number']

        if request.session.get('otp_time'):
            del request.session['otp_time']

        login(request, user)
        return redirect('home:home')

    return render(request, 'accounts/reset_password.html', {'form': form})

def login_page(request):
    if request.user.is_authenticated:
        raise Http404

    form = LoginForm(request.POST or None)

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

def author_page(request, slug):
    author = get_object_or_404(Author, slug=slug)
    return render(request, 'accounts/author.html', {'author': author})
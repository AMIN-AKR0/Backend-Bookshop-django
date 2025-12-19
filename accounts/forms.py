from django import forms
from django.contrib.auth.password_validation import validate_password
from PIL import Image
from django.contrib.auth import get_user_model
from accounts.models import Author

User = get_user_model()

class AccountForm(forms.Form):
    def clean_email(self):
        email       = self.cleaned_data.get('email')
        email_clean = email.strip().lower().replace(" ", "")

        if len(email_clean) < 10:
            self.add_error('email', 'Please enter a valid email address.')

        if len(email_clean) > 254:
            self.add_error('email', 'Please enter a valid email address.')

        if email_clean.startswith("www."):
            email_clean = email_clean[4:]

        return email_clean

    def clean_username(self):
        username       = self.cleaned_data.get('username')
        username_clean = username.strip().replace(" ", "").replace("@", "").replace("www.", "").replace("+", "").replace("-", "")

        if len(username_clean) < 5:
            self.add_error('username', 'Please enter a longer username.')

        if len(username_clean) > 30:
            self.add_error('username', 'Please enter a smaller username.')

        if username.isdigit():
            self.add_error('username', 'Username must have letters.')

        return username_clean

    def clean_password(self):
        password       = self.cleaned_data.get('password')
        password_clean = password.strip().replace(" ", "")
        return password_clean

    def clean_number(self):
        number         = self.cleaned_data.get('number')
        cleaned_number = number.strip().replace(" ", "")

        if cleaned_number.startswith(("+", "-")):
            cleaned_number = number[1:]

        if not cleaned_number.isdigit():
            self.add_error("number", "Number must be numeric.")

        if cleaned_number.startswith("98"):
            cleaned_number = cleaned_number[2:]
            cleaned_number = "0" + cleaned_number

        if not cleaned_number.startswith("09"):
            self.add_error("number", "Number must start with 09... or 98...")

        if len(cleaned_number) != 11:
            self.add_error("number", "Number must contain 11 digits.")

        return cleaned_number

    def is_email(self, email: str) -> bool:
        return "@gmail.com" in email.lower()

    def is_username(self, username: str) -> bool:
        return not "@" in username.lower() and not username.isdigit()

    def is_number(self, value: str) -> bool:
        return value.isdigit() and len(value) == 11

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')

        if not picture:
            return picture

        max_size = 4
        if picture.size > max_size * 1024 * 1024:
            self.add_error('picture', 'Image must be smaller than the 4 megabytes.')

        img = Image.open(picture)

        if img.format not in ['JPEG', 'PNG', 'GIF']:
            self.add_error('picture', 'Profile Picture must be an image.')

        return picture


class SignupForm1(AccountForm):
    number = forms.CharField(max_length=13, required=True, widget=forms.TextInput())

    def clean(self):
        number = self.clean_number()

        if User.objects.filter(number=number).exists():
            self.add_error('number', 'Number already registered.')


class SignupForm2(AccountForm):
    username  = forms.CharField(max_length=30, required=True, widget=forms.TextInput())
    password  = forms.CharField(widget=forms.PasswordInput(), max_length=50)
    password2 = forms.CharField(widget=forms.PasswordInput(), max_length=50)


    def password_chek(self, password, password2):
        if password != password2:
            return False
        else:
            return True

    def clean_password(self):
        password = self.cleaned_data['password']

        validate_password(password)
        return password


    def clean(self):

        cleaned = super().clean()

        username  = self.clean_username()
        password  = cleaned.get('password')
        password2 = cleaned.get('password2')

        if not self.password_chek(password, password2):
            self.add_error('password', "your Passwords don't match.")

        if not self.is_username(username):
            self.add_error('username', 'Invalid username.')

        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Username already registered.')


class LoginForm(AccountForm):
    number_or_username = forms.CharField(max_length=254, required=True, widget=forms.TextInput(), label="number_or_username")
    password           = forms.CharField(widget=forms.PasswordInput(), label="password", help_text="Enter your password")

    def clean(self):
        cleaned = super().clean()

        number_or_username = cleaned.get('number_or_username')

        if not number_or_username:
            self.add_error('number_or_username', 'Phone number and username are required.')
            return cleaned

        if number_or_username.startswith("+") or number_or_username.startswith("-"):
            number_or_username = number_or_username[1:]
            if number_or_username.startswith("98"):
                number_or_username = "0" + number_or_username[2:]

        if self.is_number(number_or_username):
            cleaned['number'] = number_or_username

        elif self.is_username(number_or_username):
            cleaned['username'] = number_or_username

        else:
            self.add_error('number_or_username', 'Invalid number or username.')

        cleaned.pop('number_or_username', None)
        return cleaned


class RegisterForm(AccountForm):
    number_code = forms.CharField(max_length=5, required=True, widget=forms.TextInput())

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            self.add_error('code', 'Invalid code.')
            return None
        return code.strip().replace(" ", "")


class NumberValidation(AccountForm):
    number_code = forms.CharField(max_length=5, required=True, widget=forms.TextInput(), label="number_code")

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            self.add_error('code', 'Invalid code.')
            return None
        return code.strip().replace(" ", "")


class ForgotPasswordForm(AccountForm):
    email_or_number = forms.CharField(max_length=254, required=True, widget=forms.TextInput(), label="email_or_number")

    def clean(self):
        cleaned = super().clean()

        email_or_number = cleaned.get('email_or_number')

        if email_or_number.startswith("+") or email_or_number.startswith("-"):
            email_or_number = email_or_number[1:]
            if email_or_number.startswith("98"):
                email_or_number = "0" + email_or_number[2:]

        if not email_or_number:
            self.add_error('email_or_number', 'Phone number and username are required.')

        if self.is_number(email_or_number):
            cleaned['number'] = email_or_number

        elif self.is_email(email_or_number):
            cleaned['email'] = email_or_number

        else:
            self.add_error('email_or_number', 'Invalid email or number.')

        cleaned.pop('email_or_number', None)
        return cleaned


class ResetPasswordForm(AccountForm):
    password  = forms.CharField(widget=forms.PasswordInput(), max_length=50)
    password2 = forms.CharField(widget=forms.PasswordInput(), max_length=50)

    def clean_password(self):
        password = self.cleaned_data['password']

        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()

        password  = cleaned.get('password')
        password2 = cleaned.get('password2')

        if not password or not password2:
            self.add_error('password', 'password is required.')

        if password != password2:
            self.add_error('password', "your Passwords don't match.")

        return cleaned


class ChengProfilePicForm(AccountForm):
    picture = forms.ImageField()


class AddEmailForm(AccountForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.TextInput(), label="email")


class ChangeProfileForm(AccountForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ['number', 'username', 'email']


class ChangePasswordForm(AccountForm):
    password = forms.CharField(widget=forms.PasswordInput(), max_length=50)


class ChangeAuthorInfoForm(AccountForm, forms.ModelForm):
    class Meta:
        model = Author

        fields = ['first_name', 'last_name', 'century', 'bio']
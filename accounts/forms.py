from django import forms

class AccountForm(forms.Form):
    def clean_email(self, email):
        email_clean = email.strip().lower().replace(" ", "")

        if email_clean.startswith("www."):
            email_clean = email_clean[4:]

        return email_clean

    def clean_username(self, username):
        username_clean = username.strip().replace(" ", "")
        return username_clean

    def is_email(self, email_or_username: str) -> bool:
        return "@" in email_or_username.lower()

    def is_username(self, email_or_username: str) -> bool:
        return not "@" in email_or_username.lower()

class LoginForm(AccountForm):
    email_or_username = forms.CharField(max_length=100, required=True, widget=forms.TextInput, label="email_or_username", help_text="Enter your email or username")
    password = forms.CharField(widget=forms.PasswordInput, label="password", help_text="Enter your password")
from django import forms
from accounts.forms import AccountForm

class CheckOutForm(AccountForm):
    first_name   = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your First Name'}))
    last_name    = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your Last Name'}))
    number       = forms.CharField(max_length=13, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your Phone Number'}))
    address      = forms.CharField(max_length=120, required=True, widget=forms.TextInput(attrs={'placeholder': 'city, district, street name, house number,...'}))
    postal_code  = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your Postal Code'}))

    def clean_name(self):
        first_name = self.cleaned_data.get('first_name')
        last_name  = self.cleaned_data.get('last_name')
        first_name = first_name.strip().replace(' ', '').lower()
        last_name  = last_name.strip().replace(' ', '').lower()

        if len(first_name) > 20:
            self.add_error('first_name', 'is too long.')

        if len(last_name) > 20:
            self.add_error('last_name', 'is too long.')

        if len(first_name) < 4:
            self.add_error('first_name', 'Please Enter Your First Name longer than 3 characters.')

        if len(last_name) < 4:
            self.add_error('last_name', 'Please Enter Your Last Name longer than 3 characters.')

        self.cleaned_data['name'] = first_name + ' ' + last_name

        del self.cleaned_data['first_name']
        del self.cleaned_data['last_name']

        return self.cleaned_data['name']

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        postal_code = postal_code.replace(' ', '').replace('-', '')

        if not postal_code.isdigit():
            self.add_error('postal_code', 'Postal code must be numeric.')

        if not len(str(postal_code)) == 9 and not len(str(postal_code)) == 5:
            self.add_error('postal_code', 'Postal code must be 9 or 5 digits.')

        if len(postal_code) > 20:
            self.add_error('postal_code', 'Please Enter Your Postal Code longer than 20 characters')

        return postal_code

    def clean_address(self):
        address = self.cleaned_data.get('address')

        address = address.strip().replace("\n", " ")

        if len(address) < 30:
            self.add_error('address', 'Please Enter Your Address Completely.')

        return address

    def clean(self):
        name          = self.clean_name()
        phone_number  = self.clean_number()
        address       = self.clean_address()
        postal_code   = self.clean_postal_code()

        if not name or not phone_number or not address or not postal_code:
            self.add_error('first_name', 'something went wrong.')
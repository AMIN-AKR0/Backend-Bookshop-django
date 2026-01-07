from django import forms
from accounts.forms import AccountForm
from shop.models import Book, Order


class CheckOutForm(AccountForm):
    first_name   = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your First Name'}))
    last_name    = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your Last Name'}))
    number       = forms.CharField(max_length=12, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your Phone Number'}))
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


class ChangeOrderForm(forms.ModelForm):
    class Meta:
        model  = Order

        fields = ['address', 'postal_code', 'phone_number2']

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

    def clean_phone_number2(self):
        number         = self.cleaned_data.get('phone_number2')
        cleaned_number = number.strip().replace(" ", "")

        if cleaned_number.startswith(("+", "-")):
            cleaned_number = number[1:]

        if not cleaned_number.isdigit():
            self.add_error("phone_number2", "Number must be numeric.")

        if cleaned_number.startswith("1"):
            cleaned_number = cleaned_number[1:]

        if len(cleaned_number) != 10:
            self.add_error("phone_number2", "Number must contain 10 digits.")

        return cleaned_number


class BookForm(forms.ModelForm):
    def clean_title(self):
        title = self.cleaned_data.get('title')

        if title:
            clean_title = title.strip()

            if not clean_title or len(clean_title) < 5:
                self.add_error('title', 'Title is too short.')

            return clean_title

        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')

        if description:

            clean_description = description.strip()

            if not clean_description or len(clean_description) < 60:
                self.add_error('description', 'Description is too short.')

            return clean_description

        return description

    def clean_summary(self):
        summary = self.cleaned_data.get('summary')

        if summary:
            clean_summary = summary.strip()

            if not clean_summary or len(clean_summary) < 100:
                self.add_error('summary', 'Summary is too short.')

            return clean_summary

        return summary

    def clean_pages(self):
        pages = self.cleaned_data.get('pages')

        if pages:
            if pages < 5:
                self.add_error('pages', 'Pages must be greater than or equal to 5.')

            if pages > 10000:
                self.add_error('pages', 'Pages must be less than or equal to 10000.')

        return pages

    def clean_number(self):
        number = self.cleaned_data.get('number')

        if number:
            if number < 30:
                self.add_error('number', 'Number must be greater than or equal to 30.')

        return number

    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price:
            if price > 100000:
                self.add_error('price', 'Price must be less than or equal to 10000.')

        return price

    def clean_publish_year(self):
        publish_year = self.cleaned_data.get('publish_year')

        if publish_year:
            if publish_year < 1900:
                self.add_error('publish_year', 'Publish Year must be greater than 1900.')

            if publish_year > 2026:
                self.add_error('publish_year', 'Publish Year must be lower than 2026.')

        return publish_year

    def clean_language(self):
        language = self.cleaned_data.get('language')

        if language:
            clean_language = language.strip()

            if not clean_language or len(clean_language) < 3:
                self.add_error('language', 'Language is too short.')

            return clean_language

        return language

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')

        if weight:
            if weight < 20:
                self.add_error('weight', 'Weight must be greater than or equal to 20.')

            if weight > 10000:
                self.add_error('weight', 'Weight must be less than or equal to 10000.')

        return weight

    def clean_length(self):
        length = self.cleaned_data.get('length')

        if length:
            if length < 5:
                self.add_error('length', 'Length must be greater than or equal to 5.')

            if length > 200:
                self.add_error('length', 'Length must be lower than or equal to 200.')

        return length

    def clean_width(self):
        width = self.cleaned_data.get('width')

        if width:
            if width < 5:
                self.add_error('width', 'Width must be greater than or equal to 5.')

            if width > 200:
                self.add_error('width', 'Width must be lower than or equal to 200.')

        return width


class AddBookForm(BookForm):
    length     = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Length (cm)...'}))
    width      = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Width (cm)...'}))
    image      = forms.ImageField(required=False)

    class Meta:
        model  = Book

        fields = ['title', 'description', 'price', 'summary', 'sku', 'pages', 'publish_year', 'language', 'weight', 'online_store', 'categories', 'tags', 'number']

    def clean(self):
        cleaned_data = super(AddBookForm, self).clean()

        if cleaned_data.get('length') and not cleaned_data.get('width'):
            self.add_error('width', 'If you add length, width is required.')

        if cleaned_data.get('width') and not cleaned_data.get('length'):
            self.add_error('length', 'If you add width, length is required.')

        if cleaned_data.get('length') and cleaned_data.get('width'):
            cleaned_data['dimensions'] = str(cleaned_data['length']) + ' * ' + str(cleaned_data['width'])

            cleaned_data['length'] = None
            cleaned_data['width'] = None

        return cleaned_data


class ChangeBookForm(BookForm):
    class Meta:
        model  = Book

        fields = ['description', 'price', 'summary', 'pages', 'publish_year', 'language', 'weight', 'online_store', 'tags', 'number']
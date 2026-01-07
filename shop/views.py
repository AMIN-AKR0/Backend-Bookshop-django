import datetime
import os
import time
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from Book_Shop import settings
from shop.models import Cart, CartItem, Category, Order, OrderItem, CheckOutData
from shop.models import Book, Review
from .forms import CheckOutForm, AddBookForm, ChangeBookForm, ChangeOrderForm
from django.urls import reverse
from .utils import generate_order_id, clean_old_temp_files
import stripe
from decimal import Decimal
from PIL import Image
from accounts.models import Author

stripe.api_key = settings.STRIPE_SECRET_KEY

TEMP_PATH  = 'media/shop/books/temp/'
COVER_PATH = 'media/shop/books/cover/'

fs_temp  = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'shop/books/temp/'), base_url=os.path.join(settings.MEDIA_URL, 'shop/books/temp/'))
fs_cover = FileSystemStorage(location=COVER_PATH)

# Create your views here.
def shop(request):
    books_list = Book.objects.filter(status='Active').select_related('categories')
    categories = Category.objects.order_by('-id')[:10]
    format_page = 'default'

    if request.GET.get('category'):
        category_slug = request.GET['category']
        if Category.objects.filter(slug=category_slug).exists():
            category   = Category.objects.get(slug=category_slug)
            books_list = books_list.filter(categories=category)

    if request.GET.get('sort'):
        if request.GET['sort'] == 'new':
            books_list = books_list.order_by('-created_at')
        elif request.GET['sort'] == 'old':
            books_list = books_list.order_by('created_at')
        elif request.GET['sort'] == 'low-price':
            books_list = books_list.order_by('price')
        elif request.GET['sort'] == 'high-price':
            books_list = books_list.order_by('-price')
        elif request.GET['sort'] == 'most-sale':
            books_list = books_list.order_by('-sales')
        elif request.GET['sort'] == 'low-sale':
            books_list = books_list.order_by('sales')
        elif request.GET['sort'] == 'most-rating':
            books_list = books_list.order_by('-avg_rating')
        elif request.GET['sort'] == 'low-rating':
            books_list = books_list.order_by('avg_rating')

    if request.GET.get('search'):
        search = request.GET['search']
        books_list = books_list.filter(title__icontains=search)

    if request.GET.get('format') and request.GET.get('format') == 'list':
        format_page = 'list'

    paginator = Paginator(books_list, 20)
    page      = request.GET.get('page')
    books     = paginator.get_page(page)

    return render(request, 'shop/shop.html', {'books': books, 'categories': categories, 'format': format_page})

def book_detail(request, slug):
    book         = get_object_or_404(Book, slug=slug)

    if book.status == 'Inactive':
        raise Http404

    relate_books = Book.objects.filter(categories=book.categories).exclude(id=book.id)[:4]
    reviews      = book.reviews.select_related('user__profile')

    return render(request, 'shop/book_details.html', {'book': book, 'relate_books': relate_books, 'reviews': reviews})

def add_review(request, slug):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('shop:book-detail', slug=slug)

        book    = get_object_or_404(Book, slug=slug)
        stars   = request.POST['rating']
        comment = request.POST['comment']

        if not stars:
            stars = 1

        if not book:
            return redirect('shop:book-detail', slug=slug)

        if book.reviews.filter(user=request.user).exists():
            reviews = book.reviews.filter(user=request.user)

            for review in reviews:
                review.stars = int(stars)
                review.save()

            if not comment:
                return redirect('shop:book-detail', slug=slug)

        review = Review(user=request.user, book=book, stars=stars, comment=comment)
        review.save()

        return redirect('shop:book-detail', slug=slug)

    return redirect('shop:book-detail', slug=slug)

def add_cart(request):
    if request.method != 'POST':
        return redirect('home:home')

    quantity  = request.POST['quantity']
    book_id   = request.POST['book_id']
    book      = get_object_or_404(Book, id=book_id, status='Active')
    user_cart = Cart.objects.get(user=request.user.id)

    if CartItem.objects.filter(cart=user_cart, book=book).exists():
        new_item_cart = CartItem.objects.get(cart=user_cart, book=book)

        if book.number >= int(quantity):
            new_item_cart.quantity = int(quantity)
            new_item_cart.save()

        if book.number < user_cart.items.filter(book=book).first().quantity:
            new_item_cart = CartItem.objects.get(cart=user_cart, book=book)
            new_item_cart.quantity = book.number

            new_item_cart.save()

    else:
        if book.number >= int(quantity):
            CartItem.objects.create(cart=user_cart, book=book, quantity=int(quantity))

    return redirect('shop:book-detail', slug=book.slug)

def add_cart_one(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse({'status':'not_login'})

    book      = get_object_or_404(Book, slug=slug)
    user_cart = get_object_or_404(Cart, user=request.user.id)

    for item in user_cart.items.all():
        if book == item.book:
            return JsonResponse({'status': 'exist'})

    if book.number >= 1:
        CartItem.objects.create(cart=user_cart, book=book, quantity=1)
        return JsonResponse({'status': 'added'})

    return JsonResponse({'status': 'error'})

def delete_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if CartItem.objects.filter(cart=request.user.cart, book=book).exists():
        CartItem.objects.filter(cart=request.user.cart, book=book).delete()
        return redirect('shop:cart')

    return redirect('shop:cart')

def cart(request):
    if not request.user.is_authenticated:
        return render(request, 'shop/cart.html', {'not_authenticated': True})

    user_cart  = get_object_or_404(Cart, user=request.user.id)
    cart_items = CartItem.objects.filter(cart=request.user.cart)

    for cart_item in cart_items:
        if cart_item.book.status != 'Active':
            cart_item.delete()

    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'cart': user_cart})

def checkout(request):
    if not request.user.is_authenticated:
        raise Http404

    form      = CheckOutForm(request.POST or None)
    user_cart = get_object_or_404(Cart, user=request.user)

    if user_cart.items.count() < 1:
        raise Http404

    errors = {}

    if form.is_valid():
        if form.cleaned_data['number'] == request.user.number:
            form.add_error('number', 'Please Enter Other Phone Number.')

        for item in user_cart.items.all():
            if item.quantity > item.book.number:
                errors[item.book.id] = f'There are only {item.book.number} of this book left.'

        if errors:
            return render(request, 'shop/checkout.html', {'form': form, 'cart': user_cart, 'errors': errors})

        if not form.errors and not errors:
            for item in request.user.checkout_data.all():
                item.delete()

            checkout_data = CheckOutData.objects.create(user=request.user, name=form.cleaned_data['name'], number=form.cleaned_data['number'], address=form.cleaned_data['address'], postal_code=form.cleaned_data['postal_code'])

            request.session['checkout_data'] = str(checkout_data.token)

            return redirect('shop:create_checkout_session')

    return render(request, 'shop/checkout.html', {'form': form, 'cart': user_cart, 'errors': errors})

def user_order(request):
    if not request.user.is_authenticated:
        return render(request, 'shop/orders.html', {'not_authenticated': True})

    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'shop/orders.html', {'orders': user_orders})

def order_detail(request, order_number):
    if not request.user.is_authenticated:
        raise Http404

    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    return render(request, 'shop/order_details.html', {'order': order})

def order_change(request, order_number):
    if not request.user.is_authenticated:
        raise Http404

    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if order.status == 'Canceled' or order.status == 'Transmitted' or order.status == 'Completed':
        raise Http404

    form = ChangeOrderForm(request.POST or None, instance=order)

    if form.is_valid():
        if order.status == 'Canceled' or order.status == 'Transmitted' or order.status == 'Completed':
            raise redirect('shop:orders')

        if form.cleaned_data.get('phone_number2') == order.phone_number1:
            form.add_error('phone_number2', 'Please Enter Other Phone Number.')

        if not form.errors:
            form.save()
            return redirect('shop:order-detail', order_number=order.order_number)

    return render(request, 'shop/change_order.html', {'order': order, 'form': form})

def create_checkout_session(request):
    if not request.user.is_authenticated:
        raise Http404

    user_cart     = get_object_or_404(Cart, user=request.user)

    line_items = []
    for item in user_cart.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data' : {'name' : item.book.title},
                'unit_amount': int(item.book.price * 100 + item.book.price ),
            },
            'quantity': item.quantity,
            }
        )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types= ['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('shop:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(
                reverse('shop:payment_canceled')),
        )

        return redirect(session.url, code=303)

    except:
        return redirect('shop:checkout')

def payment_success(request):
    session_id = request.GET.get('session_id')

    if not session_id or not request.user.is_authenticated:
        raise Http404

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except:
        return Http404

    if session.payment_status != 'paid':
        raise redirect('shop:checkout')

    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)

    checkout_data  = get_object_or_404(CheckOutData, token=request.session['checkout_data'])

    if not checkout_data:
        raise Http404

    user_cart  = get_object_or_404(Cart, user=request.user)
    payed_time = datetime.datetime.fromtimestamp(session.created, tz=datetime.timezone.utc)

    order = Order.objects.create(
        user          = request.user,
        order_number  = generate_order_id(),
        customer_name = checkout_data.name,
        phone_number1 = request.user.number,
        phone_number2 = checkout_data.number,
        address       = checkout_data.address,
        postal_code   = checkout_data.postal_code,
        total_amount  = Decimal(str(user_cart.get_final_price())),
        paid_at       = payed_time,
        payment_id    = payment_intent.id,
        email         = session.customer_details.email,
    )

    for item in user_cart.items.all():
        OrderItem.objects.create(
            order    = order,
            book     = item.book,
            quantity = item.quantity,
            price    = item.get_item_price(),
        )

        item.book.sales  += item.quantity
        item.book.number -= item.quantity

        item.book.save()

        if item.book.number <= 0:
            item.book.status = 'Ended'
            item.book.save()

        author_demand = item.book.price * item.quantity * 0.7

        item.book.author.demand += author_demand
        item.book.author.sale   += item.quantity
        item.book.author.save()

    user_cart.items.all().delete()
    del request.session['checkout_data']

    return redirect('shop:orders')

def payment_canceled(request):
    return redirect('shop:checkout')

def upload_book_cover(request):
    if request.method != 'POST' or not request.FILES.get('cover'):
        return redirect('blog:add_article')

    cover_file = request.FILES['cover']
    picture    = Image.open(cover_file)

    if cover_file.size > 1024 * 1024 * 3:
        return JsonResponse({'errors': {'cover': ['Cover size must be smaller than 3 MEG.']}}, status=400)

    elif picture.format not in ['JPEG', 'PNG']:
        return JsonResponse({'errors': {'cover': ['Picture must be an image']}}, status=400)

    old_cover = request.session.get('book_cover_temp_path')

    if old_cover:
        old_path = os.path.join(TEMP_PATH, os.path.basename(old_cover))

        if os.path.exists(old_path):
            os.remove(old_path)

    filename   = fs_temp.save('Book-cover_' + str(int(time.time())) + '_' + cover_file.name, cover_file)
    cover_url  = fs_temp.url(filename)
    request.session['book_cover_temp_path'] = filename
    request.session['book_cover_url']       = cover_url

    return JsonResponse({'cover_url': cover_url, 'temp_path': filename})

def add_book(request):
    if not request.user.is_authenticated and not request.user.profile.author:
        raise Http404

    if request.user.author.status == 'Inactive':
        return redirect('accounts:profile')

    clean_old_temp_files(TEMP_PATH, request=request)

    form = AddBookForm(request.POST or None, request.FILES or None)

    cover_temp_path = request.session.get('book_cover_temp_path')
    cover_url       = request.session.get('book_cover_url')

    if form.is_valid():
        if not cover_temp_path or not cover_url:
            form.add_error('image', 'The cover image is required.')

        if not form.errors:
            book            = form.save(commit=False)
            book.author     = request.user.author
            book.status     = 'Inactive'
            book.dimensions = form.cleaned_data.get('dimensions')
            book.century    = book.author.century
            book.save()

            form.save_m2m()

            src = os.path.join(TEMP_PATH, os.path.basename(cover_temp_path))

            if os.path.isfile(src):
                with open(src, 'rb') as cover_file:
                    book.image.save(os.path.basename(cover_temp_path), cover_file)

                try:
                    os.remove(src)

                except PermissionError:
                    pass

            book.save()

            request.session.pop('book_cover_temp_path', None)
            request.session.pop('book_cover_url', None)

            return redirect('shop:author_books')

    return render(request, 'shop/add_book.html', {'form': form, 'cover_url':cover_url})

def author_books(request):
    if not request.user.is_authenticated and not request.user.profile.author:
        raise Http404

    author     = get_object_or_404(Author, user=request.user)
    books_list = Book.objects.filter(author=author).order_by('-created_at')
    paginator  = Paginator(books_list, 20)
    page       = request.GET.get('page')
    books      = paginator.get_page(page)

    return render(request, 'shop/author_books.html', {'books': books})

def book_change(request, slug):
    if not request.user.is_authenticated and not request.user.profile.author:
        raise Http404

    book   = get_object_or_404(Book, slug=slug)
    author = get_object_or_404(Author, user=request.user)

    if book.author != author:
        raise Http404

    form = ChangeBookForm(request.POST or None, instance=book)

    if form.is_valid():
        if form.cleaned_data.get('number') > 0 and book.status == 'Ended':
            book.status = 'Active'
            book.save()

        form.save()

        return redirect('shop:author_books')

    return render(request, 'shop/change_book.html', {'form': form, 'book': book})
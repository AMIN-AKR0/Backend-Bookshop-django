import datetime
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from Book_Shop import settings
from shop.models import Cart, CartItem, Category, Order, OrderItem, CheckOutData
from shop.models import Book, Review
from .forms import CheckOutForm
from django.urls import reverse
from .utils import generate_order_id
import stripe
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def shop(request):
    books_list = Book.objects.all().select_related('categories')
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
    book      = get_object_or_404(Book, id=book_id)
    user_cart = Cart.objects.get(user=request.user.id)

    if CartItem.objects.filter(cart=user_cart, book=book).exists():
        new_item_cart = CartItem.objects.get(cart=user_cart, book=book)
        new_item_cart.quantity = int(quantity)
        new_item_cart.save()

    else:
        CartItem.objects.create(cart=user_cart, book=book, quantity=int(quantity))

    return redirect('shop:book-detail', slug=book.slug)

def delete_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if CartItem.objects.filter(cart=request.user.cart, book=book).exists():
        CartItem.objects.filter(cart=request.user.cart, book=book).delete()
        return redirect('shop:cart')

    return redirect('shop:cart')

def cart(request):
    if not request.user.is_authenticated:
        return render(request, 'shop/cart.html', {'not_authenticated': True})

    user_cart       = get_object_or_404(Cart, user=request.user.id)
    cart_items = CartItem.objects.filter(cart=request.user.cart)

    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'cart': user_cart})

def checkout(request):
    if not request.user.is_authenticated:
        raise Http404

    form      = CheckOutForm(request.POST or None)
    user_cart = get_object_or_404(Cart, user=request.user)

    if user_cart.items.count() < 1:
        raise Http404

    if form.is_valid():
        if form.cleaned_data['number'] == request.user.number:
            form.add_error('number', 'Please Enter Other Phone Number.')

        if not form.errors:
            for item in request.user.checkout_data.all():
                item.delete()

            checkout_data = CheckOutData.objects.create(user=request.user, name=form.cleaned_data['name'], number=form.cleaned_data['number'], address=form.cleaned_data['address'], postal_code=form.cleaned_data['postal_code'])

            request.session['checkout_data'] = str(checkout_data.token)

            return redirect('shop:create_checkout_session')

    return render(request, 'shop/checkout.html', {'form': form, 'cart': user_cart})

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

        item.book.sales += item.quantity
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
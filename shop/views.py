from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from shop.models import Cart, CartItem, Category
from shop.models import Book, Review


# Create your views here.
def shop(request):
    books_list = Book.objects.all().select_related('categories')
    categories = Category.objects.order_by('-id')[:10]
    format_page = 'default'

    if request.GET.get('format') and request.GET.get('format') == 'list':
        format_page = 'list'

    if request.GET.get('sort'):
        if request.GET['sort'] == 'new':
            books_list = books_list.order_by('-created_at')
        elif request.GET['sort'] == 'old':
            books_list = books_list.order_by('created_at')
        elif request.GET['sort'] == 'low-price':
            books_list = books_list.order_by('price')
        elif request.GET['sort'] == 'high-price':
            books_list = books_list.order_by('-price')

    if request.GET.get('category'):
        category_slug = request.GET['category']
        if Category.objects.filter(slug=category_slug).exists():
            category   = Category.objects.get(slug=category_slug)
            books_list = books_list.filter(categories=category)

    if request.GET.get('search'):
        search = request.GET['search']
        books_list = books_list.filter(title__icontains=search)

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
    cart_items = CartItem.objects.filter(cart=request.user.cart)

    return render(request, 'shop/cart.html', {'cart_items': cart_items})
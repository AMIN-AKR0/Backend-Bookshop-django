from django.db.models.aggregates import Count
from django.shortcuts import render

from accounts.models import Author
from blog.models import Article
from shop.models import Category, Book


# Create your views here.
def home(request):
    recommended_books = Book.objects.filter(status='Active')[:3]
    top_rating_books  = Book.objects.filter(status='Active').order_by('-avg_rating')[:6]
    top_sale_books    = Book.objects.filter(status='Active').order_by('-sales')[:10]
    last_books        = Book.objects.filter(status='Active').order_by('-created_at')[:10]
    authors           = Author.objects.filter(status='Active').annotate(book_count=Count('books')).order_by('-book_count')[:10]
    top_categories    = Category.objects.annotate(book_count=Count('books')).order_by('-book_count')[:20]
    articles          = Article.objects.filter(status='Public').order_by('-created')[:4]

    return render(request, 'home/home.html', {'recommended_books':recommended_books, 'top_rating_books': top_rating_books, 'top_sale_books': top_sale_books, 'last_books':last_books, 'articles': articles, 'top_categories':top_categories, 'authors':authors})

def custom_404(request, exception):
    return render(request, '404.html', status=404)
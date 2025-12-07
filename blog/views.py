from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Article, BlogCategory, ArticleView, Comment
from .utils import generate_token


# Create your views here.
def blog(request):
    articles_list    = Article.objects.all()

    if request.GET.get('category'):
        category_slug = request.GET['category']
        if BlogCategory.objects.filter(slug=category_slug).exists():
            category      = BlogCategory.objects.get(slug=category_slug)
            articles_list = articles_list.filter(category=category)

    if request.GET.get('sort'):
        if request.GET['sort'] == 'new':
            articles_list = articles_list.order_by('-created_at')
        elif request.GET['sort'] == 'old':
            articles_list = articles_list.order_by('created_at')
        elif request.GET['sort'] == 'lowest-view':
            articles_list = articles_list.order_by('views')
        elif request.GET['sort'] == 'most-view':
            articles_list = articles_list.order_by('-views')

    if request.GET.get('search'):
        search = request.GET['search']
        articles_list = articles_list.filter(title__icontains=search)

    paginator        = Paginator(articles_list, 10)
    page             = request.GET.get('page')
    articles         = paginator.get_page(page)
    categories       = BlogCategory.objects.all()[:8]
    related_articles = Article.objects.order_by('-created')

    return render(request, 'blog/blog_page.html', {'articles': articles, 'categories': categories, 'related_articles': related_articles})

def article_page(request, slug):
    article          = get_object_or_404(Article, slug=slug)
    categories       = BlogCategory.objects.all()[:8]
    related_articles = Article.objects.filter(category=article.category).order_by('-created').exclude(id=article.id)[:5]

    user_token = request.COOKIES.get('user_token')

    ip = request.META.get('REMOTE_ADDR')

    if not user_token:
        user_token = generate_token()

    allowed_view = ArticleView.objects.filter(article=article, token=user_token).exists()

    if not allowed_view:
        if request.user.is_authenticated:
            ArticleView.objects.create(article=article, user=request.user, token=user_token, ip_address=ip)
        else:
            ArticleView.objects.create(article=article, token=user_token, ip_address=ip)

    if allowed_view and request.user.is_authenticated and not ArticleView.objects.filter(article=article, token=user_token)[0].user:
        view = ArticleView.objects.filter(article=article, token=user_token)[0]
        view.user = request.user
        view.save()

    response = render(request, 'blog/article_page.html', {'article': article, 'categories': categories, 'related_articles': related_articles})
    response.set_cookie('user_token', user_token, max_age=60*60*24*360)

    return response

def add_comment(request, slug):
    if request.method == 'POST':
        user       = request.user
        message    = request.POST['message']
        article    = get_object_or_404(Article, slug=slug)

        if not article:
            return redirect('blog:blog')

        if not user or not message:
            return redirect('blog:article_page', slug=slug)

        Comment.objects.create(user=user, article=article, message=message)

        return redirect('blog:article_page', slug=slug)
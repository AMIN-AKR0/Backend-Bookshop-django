import os.path
import time
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from Book_Shop import settings
from blog.models import Article, BlogCategory, ArticleView, Comment, ImageArticle
from .utils import generate_token, clean_old_temp_files
from blog.forms import AddArticleForm, ImageArticleForm
from django.core.files.storage import FileSystemStorage
from PIL import Image
from accounts.models import Author

TEMP_PATH  = 'media/blog/article/temp/'
COVER_PATH = 'media/blog/article/cover/'
IMAGE_PATH = 'media/blog/article/image/'

fs_temp  = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'blog/article/temp/'), base_url=os.path.join(settings.MEDIA_URL, 'blog/article/temp/'))
fs_cover = FileSystemStorage(location=COVER_PATH)
fs_image = FileSystemStorage(location=IMAGE_PATH)


# Create your views here.
def blog(request):
    articles_list    = Article.objects.filter(status='Public').order_by('-created')

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
    related_articles = Article.objects.order_by('-created').filter(status='Public')

    return render(request, 'blog/blog_page.html', {'articles': articles, 'categories': categories, 'related_articles': related_articles})

def article_page(request, slug):
    article          = get_object_or_404(Article, slug=slug)

    if article.status != 'Public':
        raise Http404

    categories       = BlogCategory.objects.all()[:8]
    related_articles = Article.objects.filter(category=article.category, status='Public').order_by('-created').exclude(id=article.id)[:5]

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
        if request.user.is_authenticated:
            message    = request.POST.get('message')
            print(message)
            article    = get_object_or_404(Article, slug=slug)

            if not message or not message.strip():
                return redirect('blog:article_page', slug=slug)

            if len(message) > 200:
                message = message[:200] + '...'

            if Comment.objects.filter(user=request.user, article=article).count() > 10:
                return redirect('blog:article_page', slug=slug)

            Comment.objects.create(user=request.user, article=article, message=message)

    return redirect('blog:article_page', slug=slug)

def upload_cover(request):
    if request.method != 'POST' or not request.FILES.get('cover'):
        return redirect('blog:add_article')

    cover_file = request.FILES['cover']
    picture    = Image.open(cover_file)

    if cover_file.size > 1024 * 1024 * 3:
        return JsonResponse({'errors': {'cover': ['Cover size must be smaller than 3 MEG.']}}, status=400)

    elif picture.format not in ['JPEG', 'PNG']:
        return JsonResponse({'errors': {'cover': ['Picture must be an image']}}, status=400)

    old_cover = request.session.get('cover_temp_path')

    if old_cover:
        old_path = os.path.join(TEMP_PATH, os.path.basename(old_cover))

        if os.path.exists(old_path):
            os.remove(old_path)

    filename   = fs_temp.save('cover_' + str(int(time.time())) + '_' + cover_file.name, cover_file)
    cover_url  = fs_temp.url(filename)
    request.session['cover_temp_path'] = filename
    request.session['cover_url']       = cover_url

    return JsonResponse({'cover_url': cover_url, 'temp_path': filename})

def upload_image(request):
    if request.method != 'POST' or not request.FILES.get('image'):
        return redirect('blog:add_article')

    image_file = request.FILES['image']
    image      = Image.open(image_file)

    if image_file.size > 1024 * 1024 * 3:
        return JsonResponse({'errors': {'image' : 'Images must be smaller than 3 MEG.'}}, status=400)

    elif image.format not in ['JPEG', 'PNG']:
        return JsonResponse({'errors': {'image': ['Picture must be an image']}}, status=400)

    filename   = fs_temp.save('image_' + str(int(time.time())) + '_' + image_file.name, image_file)
    image_url  = fs_temp.url(filename)
    images     = request.session.get('images', [])
    images.append({'url': image_url, 'path': filename})
    request.session['images'] = images
    return JsonResponse({'image_url': image_url, 'path': filename})

def delete_image(request):
    if request.method != 'POST':
        return redirect('blog:add_article')

    path = request.POST.get('path')

    if not path:
        return redirect('blog:add_article')

    full_path = os.path.join(TEMP_PATH, os.path.basename(path))

    if os.path.exists(full_path):
        os.remove(full_path)

    images       = request.session.get('images', [])
    clean_images = []

    for image in images:
        if image['path'] != path:
            clean_images.append(image)

    request.session['images'] = clean_images

    return JsonResponse({'status': 'success'})

def add_article(request):
    if not request.user.is_authenticated or not request.user.profile.author:
        raise Http404

    if request.user.author.status == 'Inactive':
        return redirect('accounts:profile')

    clean_old_temp_files(TEMP_PATH, request=request)

    article_form    = AddArticleForm(request.POST or None)
    image_form      = ImageArticleForm(request.POST or None)

    cover_temp_path = request.session.get('cover_temp_path')
    cover_url       = request.session.get('cover_url')
    images          = request.session.get('images', [])

    if article_form.is_valid():
        if not cover_temp_path or not cover_url:
            article_form.add_error('cover', 'The cover image is required.')

        if len(images) > 2:
            image_form.add_error('image', 'You can only upload 2 images.')

        if not article_form.errors and not image_form.errors:
            title    = article_form.cleaned_data['title']
            content  = article_form.cleaned_data['content']
            category = article_form.cleaned_data['category']

            article  = Article.objects.create(author=request.user.author, title=title, content=content, category=category, status='Waiting')

            src = os.path.join(TEMP_PATH, os.path.basename(cover_temp_path))

            if os.path.isfile(src):
                with open(src, 'rb') as cover_file:
                    article.cover.save(os.path.basename(cover_temp_path), cover_file)

                try:
                    os.remove(src)

                except PermissionError:
                    pass

            article.save()

            for image in images:
                src = os.path.join(TEMP_PATH, os.path.basename(image['path']))
                if os.path.exists(src):
                    imge_obj = ImageArticle(article=article)

                    with open(src, 'rb') as image_file:
                        imge_obj.image.save(os.path.basename(image['path']), image_file)
                        imge_obj.save()

                    os.remove(src)

            request.session.pop('cover_temp_path', None)
            request.session.pop('cover_url', None)
            request.session.pop('images', None)

            return redirect('blog:author_articles')

    return render(request, 'blog/add_article.html', {'artocle_form': article_form, 'image_form': image_form, 'cover_url': cover_url, 'images':images})

def author_articles(request):
    if not request.user.is_authenticated or not request.user.profile.author:
        raise Http404

    author        = get_object_or_404(Author, user=request.user)

    articles_list = Article.objects.filter(author=author).order_by('-created')

    if not articles_list:
        return redirect('blog:add_article')

    paginator     = Paginator(articles_list, 10)
    page          = request.GET.get('page')
    articles      = paginator.get_page(page)

    return render(request, 'blog/author_articles.html', {'articles': articles})

def delete_author_articles(request, slug):
    if not request.user.is_authenticated or not request.user.profile.author:
        raise Http404

    author  = get_object_or_404(Author, user=request.user)
    article = get_object_or_404(Article, slug=slug, author=author)

    article.delete()

    return redirect('blog:author_articles')
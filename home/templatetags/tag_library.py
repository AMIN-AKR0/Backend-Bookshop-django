from django import template

register = template.Library()

@register.filter()
def to_int(value):
    return int(value)

@register.filter()
def to_str(value):
    return str(value)

@register.filter()
def get_cart_value(items, book):
    value = 0
    for item in items:
        if item.book != book:
            value = 1
        else:
            value = item.quantity
            break

    return value

@register.filter()
def get_item_price(item_price, quantity):
    return item_price * quantity

@register.filter()
def get_sort_name(items):
    return items.get('sort')

@register.filter()
def get_category(items, category):
    return items.get('category') == category.slug

@register.simple_tag
def update_query(request_get, **kwargs):
    qs = request_get.copy()

    for key, value in kwargs.items():
        qs[key] = value

    return qs.urlencode()

@register.simple_tag
def count_reviews(books):
    count = 0
    for book in books.all():
        count += book.reviews.all().count()

    return count

@register.simple_tag
def count_comment(articles):
    count = 0
    for article in articles.all():
        count += article.comments.count()

    return count

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key)
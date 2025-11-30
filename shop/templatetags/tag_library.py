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
def get_total_price(items):
    total = 0
    for item in items:
        total += item.book.price * item.quantity

    return total

@register.filter()
def get_final_price(items):
    total  = get_total_price(items)
    total += get_taxes(items)

    return total

@register.filter()
def get_taxes(items):
    total = get_total_price(items)
    total /= 100
    return total

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
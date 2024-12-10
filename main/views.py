from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from goods.models import Categories, Products
from goods.utils import q_search


def index(request, category_slug=None):
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', None)
    query = request.GET.get('q', None)
    goods = Products.objects.all()

    if on_sale:
        goods = goods.filter(discount__gt=0)

    if order_by and order_by != "default":
        # Ensure that `order_by` is applied only to a QuerySet
        goods = goods.order_by(order_by)

    paginator = Paginator(goods, 9)
    current_page = paginator.page(int(page))

    context = {
        'title': 'Главная - Главная',
        'content': "",
        "goods": current_page,
        "slug_url": category_slug
    }

    return render(request, 'main/index.html', context)


def about(request):
    context = {
        'title': 'Главная - О нас',
        'content': "О нас",
        'text_on_page': "Контакты: 87007737789, Почта: asd@gmail.com"
    }

    return render(request, 'main/about.html', context)
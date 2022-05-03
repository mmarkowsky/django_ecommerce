from django.shortcuts import get_object_or_404, render
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from store.models import Product, Variation
from django.core.paginator import Paginator
from django.db.models import Q


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        products_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        products_count = products.count()

    paged_products = paginado(request,products)


    context = {
        'products': paged_products,
        'products_count': products_count,
    }

    return render(request, "store/store.html", context)


def paginado(request,products):
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    return paginator.get_page(page)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug, is_available=True)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, "store/product_detail.html", context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
        else:
            products = Product.objects.all().filter(is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)
    paged_products = paginado(request,products)
    products_count = products.count()

    context = {
        'products': paged_products,
        'products_count': products_count,
    }

    return render(request, "store/store.html", context)
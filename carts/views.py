from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            try:
                variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass
            
    if request.user.is_authenticated:
        is_cart_item_exists= CartItem.objects.filter(product=product, user=request.user).exists()
        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product,user=request.user)
            ex_var_list = []
            id = []
            for item in cart_items:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
            else:
                item = CartItem.objects.create(product=product,quantity=1,user=request.user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

        else:
            item = CartItem.objects.create(product=product,quantity=1,user=request.user)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)              
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()    

        is_cart_item_exists= CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product,cart=cart)
            ex_var_list = []
            id = []
            for item in cart_items:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
            else:
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

        else:
            item = CartItem.objects.create(product=product,quantity=1,cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)            
    item.save()
    return redirect('cart')


def remove_cart(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product,user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(cart=cart, product=product)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product,user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(cart=cart, product=product)
    cart_item.delete()
    return redirect('cart')



def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart_id = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart_id, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
    except Exception as e:
        print("Produtos não se encontram disponiveis no carrinho")

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'grand_total': grand_total,
        'tax': tax
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        cart_id = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart_id, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
    
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'tax': tax
    }

    return render(request, "store/checkout.html", context)
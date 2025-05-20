from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from app_orders.models import Cart, CartItem
from app_shops.models import Shop
from .forms import ProductForm
from django.db.models import Q

def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(slug__icontains=query) |
            Q(category__name__icontains=query) |
            Q(shop__name__icontains=query)
        ).distinct()

    return render(request, 'products/products.html', {'products': products, 'query': query})

def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    in_cart = False
    is_owner = product.shop.owner == request.user

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        in_cart = CartItem.objects.filter(cart=cart, product=product).exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'in_cart': in_cart,
        'is_owner': is_owner,
    })

@login_required
def delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if product.shop.owner != request.user:
        return redirect('product_detail', slug=slug)

    if request.method == 'POST':
        product.delete()
        shop_slug = product.shop.slug
        return redirect('shop-detail', slug=shop_slug)

    return redirect('product_detail', slug=slug)

@login_required()
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if product.shop.owner != request.user:
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shop-detail', slug=product.shop.slug)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_edit.html', {'form': form, 'product': product})

@login_required
def create_product(request):
    shop_slug = request.GET.get('shop')
    shop = get_object_or_404(Shop, slug=shop_slug)

    if shop.owner != request.user:
        return redirect('shop-detail', slug=shop.slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            return redirect('shop-detail', slug=shop.slug)
    else:
        form = ProductForm()

    return render(request, 'products/product_create.html', {'form': form, 'shop': shop})

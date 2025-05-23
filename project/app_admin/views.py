from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.utils.timezone import now
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from .forms import LoginForm, ShopForm, ProductForm, CategoryForm, PickupPointForm
from app_orders.models import Order, Cart
from app_products.models import Product, Category, Review
from app_shops.models import Shop, ShopCreationRequest
from app_users.models import PickupPoints
from .forms import ReviewForm
from .tasks import send_reject_email, send_approve_email
from app_users.models import UserProfile
from .forms import UserForm, UserProfileForm
User = get_user_model()


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


def admin_login(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('app_admin:dashboard')
        else:
            form.add_error(None, 'Доступ разрешён только суперпользователям.')
    return render(request, 'admin/login.html', {'form': form})


def admin_logout(request):
    logout(request)
    return redirect('app_admin:login')


# Dashboard
@user_passes_test(is_superuser, login_url='/custom_admin/login/')
def dashboard(request):
    sections = [
        {"name": "Магазины", "url": reverse('app_admin:shop_list'), "icon": "bi-shop"},
        {"name": "Заявки", "url": reverse('app_admin:shoprequest_list'), "icon": "bi-journal-text"},
        {"name": "Пункты самовывоза", "url": reverse('app_admin:pickup_list'), "icon": "bi-geo-alt"},
        {"name": "Заказы", "url": reverse('app_admin:order_list'), "icon": "bi-basket"},
        {"name": "Товары", "url": reverse('app_admin:product_list'), "icon": "bi-box-seam"},
        {"name": "Категории", "url": reverse('app_admin:category_list'), "icon": "bi-tags"},
        {"name": "Отзывы", "url": reverse('app_admin:review_list'), "icon": "bi-chat-dots"},
        {"name": "Пользователи", "url": reverse('app_admin:user_list'), "icon": "bi-people"},
    ]
    return render(request, 'admin/dashboard.html', {"sections": sections})


def generate_crud(model, form_class, model_name, model_slug=None):
    model_slug = model_slug or model_name.lower()

    @user_passes_test(is_superuser, login_url='/custom_admin/login/')
    def list_view(request):
        items = model.objects.all()
        can_create = form_class is not None
        return render(request, 'admin/model_list.html', {
            'items': items,
            'model': model_name,
            'model_slug': model_slug,
            'can_create': can_create
        })

    @user_passes_test(is_superuser, login_url='/custom_admin/login/')
    def create_view(request):
        if form_class is None:
            return redirect(reverse(f'app_admin:{model_slug}_list'))
        form = form_class(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect(reverse(f'app_admin:{model_slug}_list'))
        return render(request, 'admin/model_create.html', {'form': form, 'model': model_name})

    @user_passes_test(is_superuser, login_url='/custom_admin/login/')
    def update_view(request, pk):
        obj = get_object_or_404(model, pk=pk)
        if form_class is None:
            return redirect(reverse(f'app_admin:{model_slug}_list'))
        form = form_class(request.POST or None, request.FILES or None, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(reverse(f'app_admin:{model_slug}_list'))
        return render(request, 'admin/model_update.html', {'form': form, 'model': model_name})

    @user_passes_test(is_superuser, login_url='/custom_admin/login/')
    def delete_view(request, pk):
        obj = get_object_or_404(model, pk=pk)
        obj.delete()
        return redirect(reverse(f'app_admin:{model_slug}_list'))

    return list_view, create_view, update_view, delete_view


shop_list, shop_create, shop_update, shop_delete = generate_crud(Shop, ShopForm, "Shop")
shoprequest_list, _, _, shoprequest_delete = generate_crud(ShopCreationRequest, None, "ShopRequest")
pickup_list, pickup_create, pickup_update, pickup_delete = generate_crud(PickupPoints, PickupPointForm, "Pickup")
order_list, _, order_update, order_delete = generate_crud(Order, None, "Order")
product_list, product_create, product_update, product_delete = generate_crud(Product, ProductForm, "Product")
category_list, category_create, category_update, category_delete = generate_crud(Category, CategoryForm, "Category")
review_list, review_create, review_update, review_delete = generate_crud(Review, ReviewForm, "Review")


@user_passes_test(is_superuser, login_url='/custom_admin/login/')
def user_list(request):
    users = User.objects.all().select_related('profile')
    return render(request, 'admin/model_list.html', {
        'items': users,
        'model': 'User',
        'model_slug': 'user',
        'can_create': False
    })


@user_passes_test(is_superuser, login_url='/custom_admin/login/')
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('app_admin:user_list')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'admin/user_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_id': user.id
    })


@user_passes_test(is_superuser, login_url='/custom_admin/login/')
def approve_shop_request(request, pk):
    request_obj = get_object_or_404(ShopCreationRequest, pk=pk)
    if request_obj.status != 'pending':
        return redirect('app_admin:shoprequest_list')

    Shop.objects.create(
        name=request_obj.name,
        slug=request_obj.slug,
        description=request_obj.description,
        logo=request_obj.logo,
        owner=request_obj.user
    )

    request_obj.status = 'approved'
    request_obj.response_time = now()
    request_obj.save()

    send_approve_email.delay(request_obj.user.username, request_obj.name, request_obj.user.email)

    return redirect('app_admin:shoprequest_list')


@user_passes_test(is_superuser, login_url='/custom_admin/login/')
def reject_shop_request(request, pk):
    request_obj = get_object_or_404(ShopCreationRequest, pk=pk)
    if request_obj.status != 'pending':
        return redirect('app_admin:shoprequest_list')

    request_obj.status = 'rejected'
    request_obj.response_time = now()
    request_obj.save()

    send_reject_email.delay(request_obj.user.username, request_obj.name, request_obj.user.email)

    return redirect('app_admin:shoprequest_list')


@user_passes_test(is_superuser, login_url='/custom_admin/login/')
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product', 'product__shop')
    return render(request, 'admin/order_detail.html', {
        'order': order,
        'items': items,
        'model': 'Order'
    })

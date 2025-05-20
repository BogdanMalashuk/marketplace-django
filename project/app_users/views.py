from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import UserRegisterForm, UserLoginForm, UserProfileUpdateForm, PhoneForm
from app_orders.models import Order

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.save()
            login(request, user)
            return redirect('products')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('products')
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('products')

@login_required
def profile_view(request):
    user = request.user
    user_profile = user.profile

    user_form = UserProfileUpdateForm(instance=user)
    phone_form = PhoneForm(instance=user_profile)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'user_form':
            user_form = UserProfileUpdateForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                return redirect('me')

        elif form_type == 'phone_form':
            phone_form = PhoneForm(request.POST, instance=user_profile)
            if phone_form.is_valid():
                phone_form.save()
                return redirect('me')

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'phone_form': phone_form,
        'user_profile': user_profile,
    })

@login_required
def pp_view(request):
    profile = request.user.profile
    orders = Order.objects.filter(pickup_point=profile.pickup_point).order_by('-created_at')

    return render(request, 'users/pp.html', {
        'orders': orders,
        'pickup_point': profile.pickup_point,
    })

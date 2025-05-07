from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .serializers import (
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer
)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from app_products.models import Product
from .forms import OrderStatusUpdateForm, OrderCreate
from django.db import transaction


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отмена заказа"""
        order = self.get_object()
        if order.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Order cannot be canceled at this stage'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'canceled'
        order.save()
        return Response({'status': 'order canceled'})

    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty")

        order = serializer.save(user=self.request.user)

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.items.all().delete()


@require_POST
@csrf_exempt
def toggle_cart_item(request):
    data = json.loads(request.body)
    product_id = data.get("product_id")
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({"success": False, "message": "Вы не авторизованы."})

    product = Product.objects.get(id=product_id)
    cart, _ = Cart.objects.get_or_create(user=user)

    cart_item = CartItem.objects.filter(cart=cart, product=product).first()

    if cart_item:
        cart_item.delete()
        return JsonResponse({"success": True, "in_cart": False})
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        return JsonResponse({"success": True, "in_cart": True})


@require_POST
def cart_remove(request):
    item_id = request.POST.get('item_id')
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart = item.cart
        item.delete()
        items = cart.items.all()
        total_price = sum(i.quantity * i.product.price for i in items)
        return JsonResponse({'success': True, 'total_price': total_price})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False}, status=404)


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in items)

    return render(request, 'orders/cart.html', {
        'cart': cart,
        'items': items,
        'total_price': total_price,
    })


@require_POST
def cart_update_quantity(request):
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')

    try:
        item = CartItem.objects.select_related('product', 'cart').get(id=item_id, cart__user=request.user)

        if action == 'increase':
            item.quantity += 1
        elif action == 'decrease':
            item.quantity -= 1

        if item.quantity <= 0:
            item.delete()
            quantity = 0
            subtotal = 0
        else:
            item.save()
            quantity = item.quantity
            subtotal = item.quantity * item.product.price

        total_price = sum(
            ci.quantity * ci.product.price
            for ci in CartItem.objects.filter(cart__user=request.user)
        )
        return JsonResponse({
            'success': True,
            'quantity': quantity,
            'subtotal': f"{subtotal:.2f}",
            'total_price': f"{total_price:.2f}"
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})


def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order-detail', order_id=order_id)  # правильно
    else:
        form = OrderStatusUpdateForm(instance=order)

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'form': form
    })


@login_required
@transaction.atomic
def order_create(request):
    cart = Cart.objects.get(user=request.user)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_items')
        form = OrderCreate(request.POST)

        if not selected_ids:
            return redirect('cart')

        selected_items = cart.items.filter(id__in=selected_ids)

        if form.is_valid():
            orders_by_shop = {}

            payment_method = form.cleaned_data['payment_method']
            pickup_point = form.cleaned_data['pickup_point']
            is_paid = payment_method == 'online'

            for item in selected_items:
                shop = item.product.shop
                if shop not in orders_by_shop:
                    orders_by_shop[shop] = {
                        'items': [],
                        'total_price': 0
                    }

                orders_by_shop[shop]['items'].append(item)
                orders_by_shop[shop]['total_price'] += item.product.price * item.quantity

            for shop, data in orders_by_shop.items():
                order = Order.objects.create(
                    user=request.user,
                    shop=shop,
                    pickup_point=pickup_point,
                    total_price=data['total_price'],
                    is_paid=is_paid,
                )

                for item in data['items']:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                    )

            return redirect('my-orders')
    else:
        form = OrderCreate()
        selected_ids = request.GET.getlist('selected_items')
        selected_items = cart.items.filter(id__in=selected_ids) if selected_ids else cart.items.all()

    return render(request, 'orders/order_create.html', {
        'form': form,
        'items': selected_items,
    })


@login_required
def my_orders_view(request):
    orders = request.user.orders.all()
    return render(request, 'orders/my_orders.html', {'orders': orders})

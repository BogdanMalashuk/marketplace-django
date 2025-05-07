from django import forms
from .models import Order, CartItem
from app_users.models import PickupPoints


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_statuses = [
            ('ready_for_pickup', 'Готов к выдаче'),
            ('delivered', 'Доставлен'),
            ('returned', 'Возвращён')
        ]
        self.fields['status'].choices = allowed_statuses


class OrderCreate(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[('online', 'Онлайн'), ('offline', 'На месте')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': ''},  # пустая строка = ничего не выводится
    )

    pickup_point = forms.ModelChoiceField(
        queryset=PickupPoints.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'required': ''},
    )

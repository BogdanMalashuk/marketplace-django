from django import forms
from .models import UserProfile, PickupPoints
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class PhoneForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']


ROLE_CHOICES = [
    ('buyer', 'Покупатель'),
    ('seller', 'Продавец'),
]


class UserProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(label='Email')
    role = forms.ChoiceField(label='Role', choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        # Предзаполнение роли из профиля
        if self.user and hasattr(self.user, 'profile'):
            self.fields['role'].initial = self.user.profile.role

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This nickname is already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This email is already taken")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        user_profile = user.profile
        user_profile.role = self.cleaned_data['role']
        user_profile.save()
        return user



class PickupPointForm(forms.ModelForm):
    class Meta:
        model = PickupPoints
        fields = ['city', 'street', 'postal_code', 'description', 'is_active']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='')
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, help_text='')
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput, help_text='')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': '',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken")
        return email

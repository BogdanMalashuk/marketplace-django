from django import forms
from .models import UserProfile, PickupPoints
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class PhoneForm(forms.ModelForm):
    """Form for updating the user's phone number in the UserProfile model."""

    class Meta:
        model = UserProfile
        fields = ['phone']


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form for updating User's username and email.
    Validates uniqueness of username and email excluding the current user instance.
    """

    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

    def clean_username(self):
        """Validate that the username is unique across users excluding the current user."""

        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This nickname is already taken")
        return username

    def clean_email(self):
        """Validate that the email is unique across users excluding the current user."""

        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This email is already taken")
        return email

    def save(self, commit=True):
        """Save the User instance with updated username and email, and save related UserProfile."""

        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        user_profile = user.profile
        user_profile.save()
        return user


class PickupPointForm(forms.ModelForm):
    """Form for creating or updating PickupPoints instances."""

    class Meta:
        model = PickupPoints
        fields = ['city', 'street', 'postal_code', 'description', 'is_active']


class UserLoginForm(AuthenticationForm):
    """User login form inheriting from Django's AuthenticationForm."""

    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class UserRegisterForm(UserCreationForm):
    """
    User registration form extending Django's UserCreationForm with email field.
    Validates email uniqueness.
    """

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
        """Validate that the email is unique across all users."""

        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken")
        return email

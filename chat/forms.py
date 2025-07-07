from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()
    picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'name', 'phone', 'email', 'picture', 'password1', 'password2']

from django import forms
from .models import *
from django.contrib.auth.models import User
from django.forms import widgets


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(label="Имя пользователя", widget=widgets.TextInput(
        attrs={"class": "form-control form-control-sm", "type": "text", "placeholder": "Введите имя пользователя"}), )
    password = forms.CharField(label="Пароль", widget=widgets.TextInput(
        attrs={"class": "form-control form-control-sm", "type": "password", "placeholder": "Введите пароль"}), )
    email = forms.CharField(label="Электронная почта", widget=widgets.TextInput(
        attrs={"type": "email", "class": "form-control form-control-sm", "id": "exampleInputEmail1",
               "aria-describedby": "emailHelp",
               "placeholder": "Введите электронную почту"}), )
    full_name = forms.CharField(label="ФИО", widget=widgets.TextInput(
        attrs={"type": "text", "class": "form-control form-control-sm", "aria-describedby": "emailHelp",
               "placeholder": "Введите ФИО"}), )
    address = forms.CharField(label="Адрес", widget=widgets.TextInput(
        attrs={"class": "form-control form-control-sm", "type": "text", "placeholder": "Введите адрес"}), )

    class Meta:
        model = User
        fields = ["username", "password", "email", "full_name", "address"]


class CustomerLoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя", widget=widgets.TextInput(
        attrs={"class": "form-control form-control-sm", "type": "text", "placeholder": "Введите имя пользователя"}), )
    password = forms.CharField(label="Пароль", widget=widgets.TextInput(
        attrs={"class": "form-control form-control-sm", "type": "password", "placeholder": "Введите пароль"}), )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'photo',  'description', 'price', 'category']

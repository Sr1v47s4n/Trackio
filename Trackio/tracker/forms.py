# tracker/forms.py

from django import forms
from .models import Website
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email")


class WebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ["url"]

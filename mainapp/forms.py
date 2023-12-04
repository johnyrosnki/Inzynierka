from django import forms
from .models import Ksiazka
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class KsiazkaForm(forms.ModelForm):
    class Meta:
        model = Ksiazka
        fields = ['tytul', 'autor', 'opis', 'okladka']

class RejestracjaForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
class KoszykForm(forms.Form):
    ilosc = forms.IntegerField(min_value=1)
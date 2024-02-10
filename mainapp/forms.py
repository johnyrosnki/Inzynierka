from django import forms
from .models import Ksiazka, ProfilUzytkownika
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

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
class ProfilUzytkownikaForm(forms.ModelForm):
    class Meta:
        model = ProfilUzytkownika
        fields = ['adres', 'kod_pocztowy', 'miasto', 'wojewodztwo']


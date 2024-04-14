from django import forms
from .models import Ksiazka, ProfilUzytkownika, Autor, Kategoria, Wydawnictwo
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
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }
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

class ZaawansowaneWyszukiwanieForm(forms.Form):
    # Definicja pól formularza
    autor = forms.CharField(required=False, label='Autor', widget=forms.TextInput(attrs={'placeholder': 'Imię i nazwisko'}))

    kategoria = forms.ModelChoiceField(queryset=Kategoria.objects.all(), required=False, label='Kategoria',
                                       empty_label="Wybierz kategorię")
    wydawnictwo = forms.ModelChoiceField(queryset=Wydawnictwo.objects.all(), required=False, label='Wydawnictwo',
                                         empty_label="Wybierz wydawnictwo")
    cena_od = forms.DecimalField(required=False, label='Cena od')
    cena_do = forms.DecimalField(required=False, label='Cena do')
    rok_wydania_od = forms.IntegerField(required=False, label='Rok wydania', min_value=1850, max_value=2024)
    typ_okladki = forms.ChoiceField(choices=[('', 'Wybierz okładkę')] + list(Ksiazka.TYP_OKLADKI_CHOICES), required=False,
                                    label='Typ okładki')



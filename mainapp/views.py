import json

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from PIL import Image, ImageOps
from .forms import KsiazkaForm
from .models import Ksiazka, Kategoria, Autor
from django.shortcuts import render, get_object_or_404
from .forms import RejestracjaForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from decimal import Decimal
from django.views import View
import json
from django.http import JsonResponse

def base(request):
    return render(request,'base.html')



def dodaj_ksiazke(request):
    if request.method == 'POST':
        form = KsiazkaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_ksiazek')  # Dodaj odpowiednią nazwę widoku
    else:
        form = KsiazkaForm()
    return render(request, 'dodaj_ksiazke.html', {'form': form})

def lista_ksiazek(request):
    ksiazki = Ksiazka.objects.all()
    for ksiazka in ksiazki:
        if ksiazka.okladka:
            # Przetwarzanie obrazu, ustawianie stałego rozmiaru (na przykład 300x300 pikseli)
            image_path = ksiazka.okladka.path
            with Image.open(image_path) as img:
                img_resized = ImageOps.fit(img, (200, 200), method=0, bleed=0.0, centering=(0.5, 0.5))
                img_resized.save(image_path)
    return render(request, 'lista_ksiazek.html', {'ksiazki': ksiazki})

def ksiazki_wedlug_kategorii(request, kategoria_id):
    kategoria = get_object_or_404(Kategoria, id=kategoria_id)
    ksiazki = Ksiazka.objects.filter(kategorie=kategoria)
    return render(request, 'ksiazki_wedlug_kategorii.html', {'kategoria': kategoria, 'ksiazki': ksiazki})

def dodaj_do_koszyka(request, ksiazka_id):
    ksiazka = Ksiazka.objects.get(pk=ksiazka_id)

    if 'koszyk' not in request.session:
        request.session['koszyk'] = {}

    koszyk = request.session['koszyk']

    if str(ksiazka_id) in koszyk:
        koszyk[str(ksiazka_id)]['ilosc'] += 1
    else:
        koszyk[str(ksiazka_id)] = {
            'tytul': ksiazka.tytul,
            'ilosc': 1,
            'cena': str(ksiazka.cena),  # Konwersja Decimal do str przed zapisaniem do sesji
            'okladka': ksiazka.okladka.url if ksiazka.okladka else None,
        }

    request.session['koszyk'] = json.loads(json.dumps(koszyk, default=str))  # Konwersja Decimal do str przed zapisaniem do sesji

    return redirect('lista_ksiazek')
# views.py
from django.shortcuts import render

def usun_z_koszyka(request, ksiazka_id):
    koszyk = request.session.get('koszyk', {})

    if str(ksiazka_id) in koszyk:
        del koszyk[str(ksiazka_id)]
        request.session['koszyk'] = koszyk

    return redirect('wyswietl_koszyk')

def wyswietl_koszyk(request):
    koszyk = request.session.get('koszyk', {})
    suma_cen = Decimal(0.0)

    for ksiazka_id, ksiazka_info in koszyk.items():
        suma_cen += Decimal(ksiazka_info['ilosc']) * Decimal(ksiazka_info['cena'])

    ksiazki_w_koszyku = []

    for ksiazka_id, ksiazka_info in koszyk.items():
        ksiazki_w_koszyku.append({
            'id': ksiazka_id,
            'tytul': ksiazka_info['tytul'],
            'ilosc': ksiazka_info['ilosc'],
            'cena': Decimal(ksiazka_info['cena']),
            'okladka': ksiazka_info.get('okladka'),
        })

    return render(request, 'wyswietl_koszyk.html', {'ksiazki_w_koszyku': ksiazki_w_koszyku, 'suma_cen': suma_cen})

def rejestracja(request):
    if request.method == 'POST':
        form = RejestracjaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logowanie')  # Przekieruj na stronę logowania po udanej rejestracji
    else:
        form = RejestracjaForm()

    return render(request, 'rejestracja.html', {'form': form})

def logowanie(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('lista_ksiazek')  # Przekieruj na stronę główną po udanym logowaniu
        else:
            messages.error(request, 'Błędne dane logowania.')

    return render(request, 'logowanie.html')


def zwieksz_ilosc(request, ksiazka_id):
    koszyk = request.session.get('koszyk', {})
    koszyk[str(ksiazka_id)]['ilosc'] += 1
    request.session['koszyk'] = koszyk
    return redirect('wyswietl_koszyk')


def zmniejsz_ilosc(request, ksiazka_id):
    koszyk = request.session.get('koszyk', {})

    if koszyk[str(ksiazka_id)]['ilosc'] > 1:
        koszyk[str(ksiazka_id)]['ilosc'] -= 1
    else:
        del koszyk[str(ksiazka_id)]  # Usuń pozycję z koszyka, jeśli ilość jest równa 1

    request.session['koszyk'] = koszyk
    return redirect('wyswietl_koszyk')



def ksiazka_szczegoly(request, slug):
    ksiazka = get_object_or_404(Ksiazka, slug=slug)
    return render(request, 'ksiazka_szczegoly.html', {'ksiazka': ksiazka})
def ksiazki_wedlug_autora(request, slug):
    autor = get_object_or_404(Autor, slug=slug)
    ksiazki_autora = autor.ksiazka_set.all()
    return render(request, 'ksiazki_wedlug_autora.html', {'autor': autor, 'ksiazki': ksiazki_autora})


class WyszukiwarkaView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        results = self.get_search_results(query)
        return JsonResponse({'results': results})

    def get_search_results(self, query):
        ksiazki = Ksiazka.objects.filter(tytul__icontains=query)
        autorzy = Autor.objects.filter(Q(imie__icontains=query) | Q(nazwisko__icontains=query))

        results = []
        for ksiazka in ksiazki:
            results.append({'label': ksiazka.tytul, 'url': ksiazka.get_absolute_url()})

        for autor in autorzy:
            results.append({'label': str(autor), 'url': autor.get_absolute_url()})

        return results




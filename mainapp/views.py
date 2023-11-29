from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from PIL import Image, ImageOps
from .forms import KsiazkaForm
from .models import Ksiazka, Kategoria
from django.shortcuts import render, get_object_or_404

def index(request):
    return HttpResponse("Witaj w aplikacji mainapp!")



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

    # Sprawdź, czy sesja koszyka już istnieje, jeśli nie, utwórz pusty koszyk
    if 'koszyk' not in request.session:
        request.session['koszyk'] = {}

    koszyk = request.session['koszyk']

    # Dodaj książkę do koszyka lub zwiększ liczbę, jeśli już tam jest
    if ksiazka_id in koszyk:
        koszyk[ksiazka_id]['ilosc'] += 1
    else:
        koszyk[ksiazka_id] = {'tytul': ksiazka.tytul, 'ilosc': 1}

    # Zapisz zmiany w sesji
    request.session['koszyk'] = koszyk

    return redirect('lista_ksiazek')
# views.py
from django.shortcuts import render

def wyswietl_koszyk(request):
    koszyk = request.session.get('koszyk', {})
    ksiazki_w_koszyku = []

    for ksiazka_id, ksiazka_info in koszyk.items():
        # Tutaj możesz dodatkowo sprawdzić, czy książka o danym ID istnieje w bazie danych
        ksiazki_w_koszyku.append({
            'tytul': ksiazka_info['tytul'],
            'ilosc': ksiazka_info['ilosc'],
            # Dodaj inne informacje, które chcesz wyświetlić
        })

    return render(request, 'koszyk.html', {'ksiazki_w_koszyku': ksiazki_w_koszyku})
def czysc_koszyk(request):
    if 'koszyk' in request.session:
        del request.session['koszyk']
    return redirect('lista_ksiazek')





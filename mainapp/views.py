import json

import stripe
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from PIL import Image, ImageOps
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from .forms import KsiazkaForm, UserEditForm, ProfilUzytkownikaForm
from .models import Ksiazka, Kategoria, Autor, Wydawnictwo, ProfilUzytkownika
from django.shortcuts import render, get_object_or_404
from .forms import RejestracjaForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from decimal import Decimal
from django.views import View
import json
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse

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
            # with Image.open(image_path) as img:
            #     img_resized = ImageOps.fit(img, (200, 200), method=0, bleed=0.0, centering=(0.5, 0.5))
            #     img_resized.save(image_path)
    return render(request, 'lista_ksiazek.html', {'ksiazki': ksiazki})



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
            'autor': f"{ksiazka.autor.imie} {ksiazka.autor.nazwisko}",
        }

    request.session['koszyk'] = json.loads(json.dumps(koszyk, default=str))  # Konwersja Decimal do str przed zapisaniem do sesji
    print(request.session['koszyk'])
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
            'autor':ksiazka_info.get('autor'),

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
def wydawnictwo_szczegoly(request, slug):
    wydawnictwo = get_object_or_404(Wydawnictwo, slug=slug)
    return render(request, 'wydawnictwo_szczegoly.html', {'wydawnictwo': wydawnictwo})
def ksiazki_wedlug_autora(request, slug):
    autor = get_object_or_404(Autor, slug=slug)
    ksiazki_autora = autor.ksiazka_set.all()
    return render(request, 'ksiazki_wedlug_autora.html', {'autor': autor, 'ksiazki': ksiazki_autora})
def ksiazki_wedlug_kategorii(request, slug):
    kategoria = get_object_or_404(Kategoria, slug=slug)
    ksiazki = Ksiazka.objects.filter(kategorie=kategoria)
    return render(request, 'ksiazki_wedlug_kategorii.html', {'kategoria': kategoria, 'ksiazki': ksiazki})


class WyszukiwarkaView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        results = self.get_search_results(query)
        return JsonResponse({'results': results})

    def get_search_results(self, query):
        ksiazki = Ksiazka.objects.filter(tytul__icontains=query)
        autorzy = Autor.objects.filter(Q(imie__icontains=query) | Q(nazwisko__icontains=query))
        wydawnictwa = Wydawnictwo.objects.filter(nazwa__icontains=query)

        results = []
        for ksiazka in ksiazki:
            results.append({'label': ksiazka.tytul, 'url': ksiazka.get_absolute_url()})

        for autor in autorzy:
            results.append({'label': autor.imie + ' ' + autor.nazwisko, 'url': autor.get_absolute_url()})

        for wydawnictwo in wydawnictwa:
            results.append({'label': wydawnictwo.nazwa, 'url': wydawnictwo.get_absolute_url()})

        return results
stripe.api_key = settings.STRIPE_SECRET_KEY



stripe.api_key = settings.STRIPE_SECRET_KEY
def inicjuj_platnosc(request):
    try:
        koszyk = request.session.get('koszyk', {})
        suma_cen = Decimal(0.0)

        # Obliczanie sumy cen na podstawie koszyka
        for ksiazka_id, ksiazka_info in koszyk.items():
            suma_cen += Decimal(ksiazka_info['ilosc']) * Decimal(ksiazka_info['cena'])

        # Tworzenie PaymentIntent z obliczoną sumą cen
        payment_intent = stripe.PaymentIntent.create(
            amount=int(suma_cen * 100),  # Kwota musi być w centach
            currency='pln',
        )

        return JsonResponse({'clientSecret': payment_intent.client_secret})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403)


def procesuj_platnosc(request):
    if request.method == "POST":
        try:
            # Pobieranie tokenu Stripe przesłanego z formularza
            token = request.POST.get("stripeToken")

            # Pobieranie sumy cen z sesji lub obliczanie jej na podstawie koszyka
            koszyk = request.session.get('koszyk', {})
            suma_cen = 0
            for ksiazka_id, ksiazka_info in koszyk.items():
                suma_cen += ksiazka_info['ilosc'] * ksiazka_info['cena']

            # Dokonanie płatności
            charge = stripe.Charge.create(
                amount=int(suma_cen * 100),  # Kwota w centach
                currency="pln",
                description="Opis płatności",
                source=token,
            )

            # Tutaj możesz dodać logikę po pomyślnej płatności, np. wysyłanie potwierdzenia e-mail

            return redirect('sukces_platnosci')  # Przekieruj do strony potwierdzającej płatność
        except stripe.error.StripeError as e:
            # Obsługa błędów płatności Stripe
            return JsonResponse({'error': str(e)}, status=403)
    else:
        return JsonResponse({"error": "Request method not allowed"}, status=405)





def dodaj_dane_platnosci(request: HttpRequest):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')

        try:
            # Tu możesz dodać logikę przetwarzania płatności z użyciem tokenu, np.:
            charge = stripe.Charge.create(
                amount=1000,  # Kwota w centach
                currency='pln',
                description='Opis transakcji',
                source=token,  # Użycie tokenu jako źródła płatności
            )

            # Przekierowanie po pomyślnej płatności lub renderowanie szablonu z potwierdzeniem
            return redirect('/potwierdz_platnosc/')

        except stripe.error.StripeError as e:
            # Obsługa błędów Stripe
            body = e.json_body
            err  = body.get('error', {})
            return render(request, 'formularz_platnosci.html', {'error': err.get('message')})

    # Dla GET, wyświetl formularz
    return render(request, 'formularz_platnosci.html')

@csrf_exempt
def zrealizuj_platnosc(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')

        try:
            # Utworzenie opłaty
            charge = stripe.Charge.create(
                amount=1000,  # Kwota w centach
                currency='pln',
                description='Opis płatności',
                source=token,  # Użycie tokenu płatności otrzymanego z formularza
            )

            return JsonResponse({'status': 'potwierdzenie', 'message': 'Płatność zrealizowana pomyślnie.'})
        except stripe.error.StripeError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Nieprawidłowe żądanie'}, status=400)

@login_required
def profil_uzytkownika(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profil_form = ProfilUzytkownikaForm(request.POST, instance=request.user.profiluzytkownika)
        if user_form.is_valid() and profil_form.is_valid():
            user_form.save()
            profil_form.save()
            return redirect('profil_uzytkownika')
    else:
        user_form = UserEditForm(instance=request.user)
        profil_form = ProfilUzytkownikaForm(instance=request.user.profiluzytkownika)
    return render(request, 'profil_uzytkownika.html', {
        'user_form': user_form,
        'profil_form': profil_form
    })


def zakladka_koszyka(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Obsługa formularza dla zalogowanego użytkownika
            try:
                profil_uzytkownika = ProfilUzytkownika.objects.get(user=request.user)
                profil_form = ProfilUzytkownikaForm(request.POST, instance=profil_uzytkownika)
                if profil_form.is_valid():
                    # Zamiast zapisywać, przechowujemy dane w sesji
                    request.session['podsumowanie_danych'] = profil_form.cleaned_data
                    return redirect('podsumowanie_danych')
            except ProfilUzytkownika.DoesNotExist:
                messages.error(request, 'Profil użytkownika nie istnieje.')
                return redirect('profil_uzytkownika')
        else:
            # Obsługa formularza dla niezalogowanego użytkownika
            profil_form = ProfilUzytkownikaForm(request.POST)
            if profil_form.is_valid():
                request.session['podsumowanie_danych'] = profil_form.cleaned_data
                return redirect('podsumowanie_danych')
            else:
                messages.error(request, 'Wystąpił błąd przy przesyłaniu danych.')
    else:
        if request.user.is_authenticated:
            # Dla zalogowanych, przekieruj od razu do podsumowania z danymi z profilu
            try:
                profil_uzytkownika = ProfilUzytkownika.objects.get(user=request.user)
                profil_form = ProfilUzytkownikaForm(instance=profil_uzytkownika)
                # Przechowaj dane w sesji
                request.session['podsumowanie_danych'] = {
                    'adres': profil_uzytkownika.adres,
                    'kod_pocztowy': profil_uzytkownika.kod_pocztowy,
                    'miasto': profil_uzytkownika.miasto,
                    'wojewodztwo': profil_uzytkownika.wojewodztwo,
                }
                return redirect('podsumowanie_danych')
            except ProfilUzytkownika.DoesNotExist:
                profil_form = ProfilUzytkownikaForm()
                user_form = UserEditForm(instance=request.user)
        else:
            profil_form = ProfilUzytkownikaForm()
            user_form = None  # Dla niezalogowanych nie pokazujemy formularza użytkownika

    context = {
        'user_form': user_form if request.user.is_authenticated else None,
        'profil_form': profil_form,
        'zalogowany': request.user.is_authenticated,
    }

    return render(request, 'podsumowanie.html', context)

def podsumowanie_danych(request):
    # Pobieranie danych do wysyłki z sesji
    dane = request.session.get('podsumowanie_danych', None)
    if dane is None:
        messages.error(request, 'Brak danych do wyświetlenia.')
        return redirect('lista_ksiazek')

    # Pobieranie danych o książkach w koszyku
    koszyk = request.session.get('koszyk', {})
    ksiazki_w_koszyku = []
    suma_cen = Decimal('0.00')

    for ksiazka_id, ksiazka_info in koszyk.items():
        cena_za_pozycje = Decimal(ksiazka_info['cena']) * ksiazka_info['ilosc']
        suma_cen += cena_za_pozycje
        ksiazki_w_koszyku.append({
            'tytul': ksiazka_info['tytul'],
            'autor': ksiazka_info['autor'],
            'ilosc': ksiazka_info['ilosc'],
            'cena': ksiazka_info['cena'],
            'cena_za_pozycje': cena_za_pozycje,
        })

    # Przekazywanie danych do wysyłki oraz informacji o książkach i ich łącznej cenie do szablonu
    context = {
        'dane': dane,
        'ksiazki_w_koszyku': ksiazki_w_koszyku,
        'suma_cen': suma_cen,
    }

    return render(request, 'podsumowanie_danych.html', context)



#Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class SesjaStripe(View):
    def post(self, request, *args, **kwargs):
        koszyk = request.session.get('koszyk', [])

        line_items = [
            {
                "price_data": {
                    "currency": "pln",
                    "unit_amount": int(float(ksiazka_info['cena']) * 100),
                    "product_data": {
                        "name": ksiazka_info['tytul'],
                        "description": ksiazka_info['autor'],
                        # Zakomentowane, ponieważ wymaga konfiguracji URL obrazka
                       # "media": ksiazka_info.get('okladka')],
                    },
                },
                "quantity": ksiazka_info['ilosc'],
            } for ksiazka_id, ksiazka_info in koszyk.items()
        ]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )

        return redirect(checkout_session.url)

class Sukces(TemplateView):
    template_name = "potwierdzenie.html"

class Anulowanie(TemplateView):
    template_name = "anulowanie.html"

stripe.api_key = settings.STRIPE_SECRET_KEY

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook view to handle checkout session completed event.
    """

    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            print("Płatność pomyślnie zrealizowana")

        # Can handle other events here.

        return HttpResponse(status=200)
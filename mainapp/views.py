import json

import stripe
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Sum, Count
from django.shortcuts import render
from django.utils import timezone
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from PIL import Image, ImageOps
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, FormView
from collections import Counter

from .forms import KsiazkaForm, UserEditForm, ProfilUzytkownikaForm, ZaawansowaneWyszukiwanieForm
from .models import Ksiazka, Kategoria, Autor, Wydawnictwo, ProfilUzytkownika, Zamowienie, PozycjaZamowienia, \
    PrzegladaneKsiazki
from django.shortcuts import render, get_object_or_404
from .forms import RejestracjaForm
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from decimal import Decimal
from django.views import View
import json
from django.http import JsonResponse
from django.conf import settings
from itertools import chain

from django.urls import reverse
from django.contrib.auth.models import User


def base(request):
    rekomendacje = rekomendacje_zakupy()

    return render(request, 'base.html', {'rekomendacje': rekomendacje})



def dodaj_ksiazke(request):
    if request.method == 'POST':
        form = KsiazkaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_ksiazek')
    else:
        form = KsiazkaForm()
    return render(request, 'dodaj_ksiazke.html', {'form': form})

def lista_ksiazek(request):
    ksiazki = Ksiazka.objects.all()
    for ksiazka in ksiazki:
        if ksiazka.okladka:
            image_path = ksiazka.okladka.path
    paginator = Paginator(ksiazki, 18)
    page = request.GET.get('page')
    try:
        ksiazki = paginator.page(page)
    except PageNotAnInteger:

        ksiazki = paginator.page(1)
    except EmptyPage:

        ksiazki = paginator.page(paginator.num_pages)
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
            'cena': str(ksiazka.cena),
            'okladka': ksiazka.okladka.url if ksiazka.okladka else None,
            'autor': f"{ksiazka.autor.imie} {ksiazka.autor.nazwisko}",
        }
    request.session['koszyk'] = json.loads(json.dumps(koszyk, default=str))
    return redirect('lista_ksiazek')


def usun_z_koszyka(request, ksiazka_id):
    koszyk = request.session.get('koszyk', {})

    if str(ksiazka_id) in koszyk:
        del koszyk[str(ksiazka_id)]
        request.session['koszyk'] = koszyk

    return redirect('wyswietl_koszyk')


def wyswietl_koszyk(request):
    koszyk = request.session.get('koszyk', {})
    suma_cen = Decimal(0.0)
    if request.user.is_authenticated:

        rekomendacje_ksiazek = generuj_rekomendacje(request.user)
    else:

        rekomendacje_ksiazek = None
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

    return render(request, 'wyswietl_koszyk.html', {'ksiazki_w_koszyku': ksiazki_w_koszyku, 'suma_cen': suma_cen,'rekomendacje':rekomendacje_ksiazek})

def rejestracja(request):
    if request.method == 'POST':
        form = RejestracjaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logowanie')
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
            return redirect('lista_ksiazek')
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
        del koszyk[str(ksiazka_id)]

    request.session['koszyk'] = koszyk
    return redirect('wyswietl_koszyk')



def ksiazka_szczegoly(request, slug):
    ksiazka = get_object_or_404(Ksiazka, slug=slug)
    if request.user.is_authenticated:

        przegladana_ksiazka, created = PrzegladaneKsiazki.objects.get_or_create(
            user=request.user,
            ksiazka=ksiazka,
            defaults={'data_przegladania': timezone.now()}
        )

        if not created:

            przegladana_ksiazka.data_przegladania = timezone.now()
            przegladana_ksiazka.save()


        przegladane_ksiazki = PrzegladaneKsiazki.objects.filter(user=request.user).order_by('-data_przegladania')
        if przegladane_ksiazki.count() > 10:

            najstarsze_id_do_usuniecia = przegladane_ksiazki[10:].values_list('id', flat=True)
            PrzegladaneKsiazki.objects.filter(id__in=list(najstarsze_id_do_usuniecia)).delete()

    return render(request, 'ksiazka_szczegoly.html', {'ksiazka': ksiazka})
def wydawnictwo_szczegoly(request, slug):
    wydawnictwo = get_object_or_404(Wydawnictwo, slug=slug)

    ksiazki = Ksiazka.objects.filter(wydawnictwo=wydawnictwo)
    return render(request, 'wydawnictwo_szczegoly.html', {
        'wydawnictwo': wydawnictwo,
        'ksiazki': ksiazki
    })
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
        kategoria = Kategoria.objects.filter(nazwa__icontains=query)

        results = []
        for ksiazka in ksiazki:
            results.append({'label': ksiazka.tytul, 'url': ksiazka.get_absolute_url()})

        for autor in autorzy:
            results.append({'label': autor.imie + ' ' + autor.nazwisko, 'url': autor.get_absolute_url()})

        for wydawnictwo in wydawnictwa:
            results.append({'label': wydawnictwo.nazwa, 'url': wydawnictwo.get_absolute_url()})

        for kategorie in kategoria:
            results.append({'label': kategorie.nazwa, 'url': kategorie.get_absolute_url()})

        return results


@csrf_exempt
def zrealizuj_platnosc(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')

        try:

            charge = stripe.Charge.create(
                amount=1000,
                currency='pln',
                description='Opis płatności',
                source=token,
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
            messages.success(request, 'Profil został pomyślnie zaktualizowany.')
            return redirect('profil_uzytkownika')
    else:
        user_form = UserEditForm(instance=request.user)
        profil_form = ProfilUzytkownikaForm(instance=request.user.profiluzytkownika)
    pozycje_zamowien = PozycjaZamowienia.objects.filter(zamowienie__user=request.user,
                                                        zamowienie__zaplacone=True).select_related('zamowienie',
                                                                                                   'zamowienie__user')
    return render(request, 'profil_uzytkownika.html', {
        'user_form': user_form,
        'profil_form': profil_form,
        'pozycje_zamowien': pozycje_zamowien
    })


def zakladka_koszyka(request):
    if request.method == 'POST':
        if request.user.is_authenticated:

            try:
                profil_uzytkownika = ProfilUzytkownika.objects.get(user=request.user)
                profil_form = ProfilUzytkownikaForm(request.POST, instance=profil_uzytkownika)
                if profil_form.is_valid():

                    request.session['podsumowanie_danych'] = profil_form.cleaned_data
                    return redirect('podsumowanie_danych')
            except ProfilUzytkownika.DoesNotExist:
                messages.error(request, 'Profil użytkownika nie istnieje.')
                return redirect('profil_uzytkownika')
        else:

            profil_form = ProfilUzytkownikaForm(request.POST)
            if profil_form.is_valid():
                request.session['podsumowanie_danych'] = profil_form.cleaned_data
                return redirect('podsumowanie_danych')
            else:
                messages.error(request, 'Wystąpił błąd przy przesyłaniu danych.')
    else:
        if request.user.is_authenticated:

            try:
                profil_uzytkownika = ProfilUzytkownika.objects.get(user=request.user)
                profil_form = ProfilUzytkownikaForm(instance=profil_uzytkownika)

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
            user_form = None

    context = {
        'user_form': user_form if request.user.is_authenticated else None,
        'profil_form': profil_form,
        'zalogowany': request.user.is_authenticated,
    }

    return render(request, 'podsumowanie.html', context)

def podsumowanie_danych(request):

    dane = request.session.get('podsumowanie_danych', None)
    if dane is None:
        messages.error(request, 'Brak danych do wyświetlenia.')
        return redirect('lista_ksiazek')


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


    context = {
        'dane': dane,
        'ksiazki_w_koszyku': ksiazki_w_koszyku,
        'suma_cen': suma_cen,
    }

    return render(request, 'podsumowanie_danych.html', context)



stripe.api_key = settings.STRIPE_SECRET_KEY


class SesjaStripe(View):
    def post(self, request, *args, **kwargs):
        koszyk = request.session.get('koszyk', [])
        user = request.user
        try:
            profil_uzytkownika = ProfilUzytkownika.objects.get(user=user)
            if not all([ profil_uzytkownika.adres, profil_uzytkownika.kod_pocztowy, profil_uzytkownika.miasto, profil_uzytkownika.wojewodztwo]):
                messages.error(request,
                               "Proszę uzupełnić wszystkie wymagane dane w profilu przed przejściem do płatności.")
                return redirect('profil_uzytkownika')

        except ProfilUzytkownika.DoesNotExist:
            messages.error(request, "Proszę uzupełnić profil.")
            return redirect('profil_uzytkownika')

        nowe_zamowienie = Zamowienie.objects.create(
            user=user,
            zaplacone=False,
            adres=profil_uzytkownika.adres,
            kod_pocztowy=profil_uzytkownika.kod_pocztowy,
            miasto=profil_uzytkownika.miasto,
            wojewodztwo=profil_uzytkownika.wojewodztwo,

        )

        line_items = [
            {
                "price_data": {
                    "currency": "pln",
                    "unit_amount": int(float(ksiazka_info['cena']) * 100),
                    "product_data": {
                        "name": ksiazka_info['tytul'],
                        "description": ksiazka_info['autor'],
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
            metadata={
                'order_id': str(nowe_zamowienie.id),
                'user_id': str(user.id)
            }
        )

        for ksiazka_id, ksiazka_info in koszyk.items():
            ksiazka = Ksiazka.objects.get(id=ksiazka_id)
            PozycjaZamowienia.objects.create(

                zamowienie=nowe_zamowienie,
                ksiazka=ksiazka,
                ilosc=ksiazka_info['ilosc'],
                cena=ksiazka_info['cena']
            )

            request.session['koszyk'] = {}

        return redirect(checkout_session.url)

class Sukces(TemplateView):
    template_name = "potwierdzenie.html"

class Anulowanie(TemplateView):
    template_name = "anulowanie.html"

stripe.api_key = settings.STRIPE_SECRET_KEY

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:

            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:

            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')
            user_id = session.get('metadata', {}).get('user_id')

            if order_id:
                try:
                    zamowienie = Zamowienie.objects.get(id=order_id)
                    zamowienie.zaplacone = True
                    zamowienie.save()


                    user_sessions = Session.objects.filter(session_data__contains=f'"_auth_user_id":"{user_id}"')
                    for session in user_sessions:
                        session_data = session.get_decoded()
                        session_data.pop('koszyk', None)
                        session.session_data = json.dumps(session_data)
                        session.save()

                    return HttpResponse(status=203)

                except Zamowienie.DoesNotExist:
                    return HttpResponse(status=403)

        return HttpResponse(status=201)

def szczegoly_ksiazki(request, pk):
    ksiazka = get_object_or_404(Ksiazka, pk=pk)
    if request.user.is_authenticated:
        PrzegladaneKsiazki.objects.filter(user=request.user, ksiazka=ksiazka).delete()
        PrzegladaneKsiazki.objects.create(user=request.user, ksiazka=ksiazka)

        przegladane_ksiazki = PrzegladaneKsiazki.objects.filter(user=request.user).order_by('-data_przegladania')
        if przegladane_ksiazki.count() > 10:
            najstarsza_ksiazka_do_usuniecia = przegladane_ksiazki.last()
            najstarsza_ksiazka_do_usuniecia.delete()
    return redirect('szczegoly_ksiazki', pk=pk)

@login_required
def historia_przegladanych_ksiazek(request):
    przegladane_ksiazki = PrzegladaneKsiazki.objects.filter(user=request.user)[:10]
    return render(request, 'historia_przegladanych_ksiazek.html', {'przegladane_ksiazki': przegladane_ksiazki})




def generuj_rekomendacje(user):

    zamowione_ksiazki = PozycjaZamowienia.objects.filter(
        zamowienie__user=user, zamowienie__zaplacone=True
    ).select_related('ksiazka').values_list('ksiazka__id', 'ksiazka__autor', 'ksiazka__kategorie')

    przegladane_ksiazki = PrzegladaneKsiazki.objects.filter(user=user).select_related('ksiazka').values_list(
        'ksiazka__id', 'ksiazka__autor', 'ksiazka__kategorie')
    wszystkie_ksiazki = list(chain(zamowione_ksiazki, przegladane_ksiazki))

    znane_ksiazki_ids = {ksiazka_id for ksiazka_id, _, _ in wszystkie_ksiazki}

    autor_i_kategoria_counter = Counter((autor, kategoria) for _, autor, kategoria in wszystkie_ksiazki)
    ksiazki_do_rekomendacji = []

    for (autor, kategoria), _ in autor_i_kategoria_counter.most_common():
        if len(ksiazki_do_rekomendacji) >= 10:
            break
        potencjalne_ksiazki = Ksiazka.objects.filter(
            autor=autor, kategorie=kategoria
        ).exclude(id__in=znane_ksiazki_ids).distinct()

        for ksiazka in potencjalne_ksiazki:
            if len(ksiazki_do_rekomendacji) < 10:
                ksiazki_do_rekomendacji.append(ksiazka)
                znane_ksiazki_ids.add(ksiazka.id)

    if len(ksiazki_do_rekomendacji) < 10:
        kategoria_counter = Counter(kategoria for _, _, kategoria in wszystkie_ksiazki)
        for kategoria, _ in kategoria_counter.most_common():
            if len(ksiazki_do_rekomendacji) >= 10:
                break
            potencjalne_ksiazki = Ksiazka.objects.filter(
                kategorie=kategoria
            ).exclude(id__in=znane_ksiazki_ids).distinct()

            for ksiazka in potencjalne_ksiazki:
                if len(ksiazki_do_rekomendacji) < 10:
                    ksiazki_do_rekomendacji.append(ksiazka)
                    znane_ksiazki_ids.add(ksiazka.id)

    return ksiazki_do_rekomendacji[:10]



@login_required
def rekomendacje(request):
    rekomendacje_ksiazek = generuj_rekomendacje(request.user)
    return render(request, 'rekomendacje.html', {'rekomendacje': rekomendacje_ksiazek})


def zaawansowane_wyszukiwanie(request):
    form = ZaawansowaneWyszukiwanieForm(request.GET or None)
    results = []

    if form.is_valid():
        cleaned_data = form.cleaned_data
        qs = Ksiazka.objects.all()

        if cleaned_data.get('rok_wydania_od'):
            qs = qs.filter(rok_wydania__gte=cleaned_data['rok_wydania_od'])

        if cleaned_data.get('cena_od'):
            qs = qs.filter(cena__gte=cleaned_data['cena_od'])
        if cleaned_data.get('cena_do'):
            qs = qs.filter(cena__lte=cleaned_data['cena_do'])

        if cleaned_data.get('typ_okladki') and cleaned_data['typ_okladki'] != '':
            qs = qs.filter(typ_okladki=cleaned_data['typ_okladki'])

        if cleaned_data.get('autor'):

            autor_parts = cleaned_data['autor'].split()
            if len(autor_parts) == 1:

                qs = qs.filter(Q(autor__imie__icontains=autor_parts[0]) | Q(autor__nazwisko__icontains=autor_parts[0]))
            elif len(autor_parts) > 1:

                qs = qs.filter(autor__imie__icontains=autor_parts[0], autor__nazwisko__icontains=autor_parts[1])


        if cleaned_data.get('kategoria'):
            qs = qs.filter(kategorie__nazwa__icontains=cleaned_data['kategoria'])


        if cleaned_data.get('wydawnictwo'):
            qs = qs.filter(wydawnictwo__nazwa__icontains=cleaned_data['wydawnictwo'])


        results = qs

    return render(request, 'zaawansowane_wyszukiwanie.html', {'form': form, 'results': results})


def rekomendacje_zakupy():

    najpopularniejsze_ksiazki = PozycjaZamowienia.objects.filter(
        zamowienie__zaplacone=True
    ).values(
        'ksiazka', 'ksiazka__tytul', 'ksiazka__slug', 'ksiazka__okladka', 'ksiazka__cena', 'ksiazka__id'
    ).annotate(
        total=Count('ksiazka')
    ).order_by('-total')[:10]

    for ksiazka in najpopularniejsze_ksiazki:
        if ksiazka['ksiazka__okladka']:
            ksiazka['okladka_url'] = settings.MEDIA_URL + str(ksiazka['ksiazka__okladka'])
        ksiazka['cena'] = ksiazka['ksiazka__cena']

    return list(najpopularniejsze_ksiazki)



def wszystkie_sprzedane_ksiazki(request):
    sprzedane_ksiazki = PozycjaZamowienia.objects.filter(
        zamowienie__zaplacone=True
    ).values(
        'ksiazka__tytul', 'ksiazka__autor', 'ksiazka__id'
    ).annotate(
        ilosc_sprzedanych=Count('id')
    ).order_by('-ilosc_sprzedanych')

    return render(request, 'sprzedane_ksiazki.html', {'sprzedane_ksiazki': sprzedane_ksiazki})
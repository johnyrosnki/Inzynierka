from idlelib import query

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.text import slugify


class Kategoria(models.Model):
    nazwa = models.CharField(max_length=100)

    def __str__(self):
        return self.nazwa
class Ksiazka(models.Model):
    tytul = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    opis = models.TextField()
    okladka = models.ImageField(upload_to='okladki/', null=True, blank=True)
    kategorie = models.ManyToManyField(Kategoria)
    cena = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)





    def __str__(self):
        return self.tytul
def lista_ksiazek(request):

    ksiazki = Ksiazka.objects.all()
    return render(request, 'lista_ksiazek.html', {'ksiazki': ksiazki})

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

def wyswietl_koszyk(request):
    koszyk = request.session.get('koszyk', {})
    return render(request, 'wyswietl_koszyk.html', {'koszyk': koszyk})
class Zakladka(models.Model):

    ksiazka = models.ForeignKey(Ksiazka, on_delete=models.CASCADE)
    data_dodania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ksiazka.tytul}"

@receiver(post_save, sender=Ksiazka)

def dodaj_zakladke_po_dodaniu_ksiazki(sender, instance, created, **kwargs):
    if created:
        # Jeśli nowa książka została utworzona, dodaj zakładkę
        Zakladka.objects.create( ksiazka=instance)

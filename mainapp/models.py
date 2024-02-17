from idlelib import query

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from unidecode import unidecode
from django.views import View


class Kategoria(models.Model):
    nazwa = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    def save(self, *args, **kwargs):

        self.slug = slugify(self.nazwa)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ksiazki_wedlug_kategorii', args=[self.slug])

    def __str__(self):
        return self.nazwa
class Autor(models.Model):
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.imie} {self.nazwisko}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ksiazki_wedlug_autora', args=[self.slug])

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
class Wydawnictwo(models.Model):
    nazwa = models.CharField(max_length=100)
    opis = models.TextField()
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):

        self.slug = slugify(self.nazwa)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('wydawnictwo_szczegoly', args=[self.slug])
    def __str__(self):
        return self.nazwa



class Ksiazka(models.Model):
    tytul = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    opis = models.TextField()
    okladka = models.ImageField(upload_to='okladki/', null=True, blank=True)
    kategorie = models.ManyToManyField(Kategoria)
    cena = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    data_utworzenia = models.DateTimeField(default=timezone.now, verbose_name="Data utworzenia")
    wydawnictwo = models.ForeignKey(Wydawnictwo, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.tytul)
        super().save(*args, **kwargs)

    def get_absolute_url(self):

        return reverse('ksiazka_szczegoly', args=[str(self.slug)])


@receiver(pre_save, sender=Ksiazka)
def generate_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.tytul)




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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=1)

    def __str__(self):
        return f"{self.user.username} - {self.ksiazka.tytul}"

@receiver(post_save, sender=Ksiazka)

def dodaj_zakladke_po_dodaniu_ksiazki(sender, instance, created, **kwargs):
    if created:
        # Jeśli nowa książka została utworzona, dodaj zakładkę
        Zakladka.objects.create( ksiazka=instance)



class ProfilUzytkownika(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adres = models.CharField(max_length=255, blank=True)
    kod_pocztowy = models.CharField(max_length=10, blank=True)
    miasto = models.CharField(max_length=100, blank=True)
    wojewodztwo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Zamowienie(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Użytkownik")
    zaplacone = models.BooleanField(default=False, verbose_name="Zapłacone")
    adres = models.CharField(max_length=255, verbose_name="Adres", default="nazwa")
    kod_pocztowy = models.CharField(max_length=10, verbose_name="Kod pocztowy",default="111")
    miasto = models.CharField(max_length=100, verbose_name="Miasto",default="nazwa")
    wojewodztwo = models.CharField(max_length=100, verbose_name="Województwo",default="nazwa")


    def __str__(self):
        return f"Zamówienie {self.id} użytkownika {self.user.username} - {'zapłacone' if self.zaplacone else 'niezapłacone'}"

    class Meta:
        verbose_name = "Zamówienie"
        verbose_name_plural = "Zamówienia"

class PozycjaZamowienia(models.Model):
    zamowienie = models.ForeignKey(Zamowienie, related_name='pozycje', on_delete=models.CASCADE, verbose_name="Zamówienie")
    ksiazka = models.ForeignKey(Ksiazka, on_delete=models.CASCADE, verbose_name="Książka",default=16)  # Dodane
    ilosc = models.PositiveIntegerField(verbose_name="Ilość")
    cena = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cena za sztukę")

    def __str__(self):
        return f"Pozycja: {self.ksiazka.tytul} x {self.ilosc} w zamówieniu {self.zamowienie.id}"

    class Meta:
        verbose_name = "Pozycja zamówienia"
        verbose_name_plural = "Pozycje zamówienia"

class PrzegladaneKsiazki(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ksiazka = models.ForeignKey(Ksiazka, on_delete=models.CASCADE)
    data_przegladania = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_przegladania']
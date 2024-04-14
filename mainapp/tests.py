from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.test import TestCase

from mainapp.models import Ksiazka, Autor, Wydawnictwo


class KoszyktTestCase(TestCase):


    def setUp(self):
        # Utworzenie przykładowego autora
        autor = Autor.objects.create(imie="Jan", nazwisko="Kowalski")
        # Utworzenie przykładowego wydawnictwa
        wydawnictwo = Wydawnictwo.objects.create(nazwa="Prószyński i S-ka")
        # Utworzenie przykładowego użytkownika
        uzytkownik = User.objects.create_user('jankowalski', 'jan@example.com', 'janspassword')

        # Utworzenie przykładowej książki w bazie danych
        self.ksiazka = Ksiazka.objects.create(tytul="Testowa Książka", cena=29.99, autor=autor, wydawnictwo=wydawnictwo)
        self.client = Client()



    def test_dodaj_do_koszyka(self):
        response = self.client.post(reverse('dodaj_do_koszyka', args=[self.ksiazka.pk]))
        self.assertEqual(response.status_code, 302)  # oczekiwane przekierowanie na listę książek

        # Sprawdzenie, czy książka została dodana do koszyka w sesji
        koszyk = self.client.session.get('koszyk')
        self.assertIsNotNone(koszyk)
        self.assertIn(str(self.ksiazka.pk), koszyk)
        self.assertEqual(koszyk[str(self.ksiazka.pk)]['ilosc'], 1)


class RejestracjaTestCase(TestCase):
    def test_rejestracja(self):
        response = self.client.post(reverse('rejestracja'), data={
            'username': 'nowyuser',
            'password1': 'trudnehaslo123',
            'password2': 'trudnehaslo123',
            'email': 'user@example.com'
        })
        self.assertRedirects(response, reverse('logowanie'))
        # Sprawdzenie, czy użytkownik został stworzony
        user = User.objects.filter(username='nowyuser').exists()
        self.assertTrue(user)


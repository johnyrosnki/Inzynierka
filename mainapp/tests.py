from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.test import TestCase

from mainapp.forms import KsiazkaForm
from mainapp.models import Ksiazka, Autor, Wydawnictwo, Kategoria, Zakladka, ProfilUzytkownika, PozycjaZamowienia, \
    Zamowienie


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
        self.add_url = reverse('dodaj_do_koszyka', args=[self.ksiazka.pk])
        self.remove_url = reverse('usun_z_koszyka', args=[self.ksiazka.pk])



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
class WydawnictwoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Tworzenie obiektu Wydawnictwo, który będzie dostępny w każdym teście
        Wydawnictwo.objects.create(nazwa='Wydawnictwo Testowe', opis='opisa')

    def test_nazwa_label(self):
        wydawnictwo = Wydawnictwo.objects.get(id=1)
        field_label = wydawnictwo._meta.get_field('nazwa').verbose_name
        self.assertEquals(field_label, 'nazwa')

    def test_opis_label(self):
        wydawnictwo = Wydawnictwo.objects.get(id=1)
        field_label = wydawnictwo._meta.get_field('opis').verbose_name
        self.assertEquals(field_label, 'opis')

    def test_string_representation(self):
        wydawnictwo = Wydawnictwo.objects.get(id=1)
        expected_object_name = f'{wydawnictwo.nazwa}'
        self.assertEquals(str(wydawnictwo), expected_object_name)


class AutorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Utworzenie obiektu Autor do użycia we wszystkich metodach testowych
        Autor.objects.create(imie="Jan", nazwisko="Kowalski")

    def test_imie_label(self):
        autor = Autor.objects.get(id=1)
        field_label = autor._meta.get_field('imie').verbose_name
        self.assertEquals(field_label, 'imie')

    def test_nazwisko_label(self):
        autor = Autor.objects.get(id=1)
        field_label = autor._meta.get_field('nazwisko').verbose_name
        self.assertEquals(field_label, 'nazwisko')

    def test_object_name_is_imie_nazwisko(self):
        autor = Autor.objects.get(id=1)
        expected_object_name = f"{autor.imie} {autor.nazwisko}"
        self.assertEquals(expected_object_name, str(autor))

    def test_imie_max_length(self):
        autor = Autor.objects.get(id=1)
        max_length = autor._meta.get_field('imie').max_length
        self.assertEquals(max_length, 100)

    def test_nazwisko_max_length(self):
        autor = Autor.objects.get(id=1)
        max_length = autor._meta.get_field('nazwisko').max_length
        self.assertEquals(max_length, 100)

    class ZamowienieModelTests(TestCase):
        @classmethod
        def setUpTestData(cls):
            cls.user = User.objects.create_user(username='testuser', password='12345')

            # Utwórz książkę
            autor = Autor.objects.create(imie='Jan', nazwisko='Nowak')
            wydawnictwo = Wydawnictwo.objects.create(nazwa='Wydawnictwo Testowe', opis='Opis testowego wydawnictwa')
            cls.ksiazka = Ksiazka.objects.create(
                tytul='Przykladowa Ksiazka',
                autor=autor,
                opis='Opis testowej ksiazki',
                cena=39.99,
                wydawnictwo=wydawnictwo
            )

            # Utwórz zamówienie
            cls.zamowienie = Zamowienie.objects.create(
                user=cls.user,
                adres='Testowa ulica 123',
                kod_pocztowy='00-000',
                miasto='Testowe Miasto',
                wojewodztwo='Testowe Województwo'
            )

        def test_zamowienie_creation(self):
            self.assertTrue(isinstance(self.zamowienie, Zamowienie))
            self.assertEqual(self.zamowienie.__str__(), f"Zamówienie {self.zamowienie.id} użytkownika {self.user.username} - niezapłacone")

        def test_zamowienie_with_pozycja(self):

            PozycjaZamowienia.objects.create(
                zamowienie=self.zamowienie,
                ksiazka=self.ksiazka,
                ilosc=1,
                cena=self.ksiazka.cena
            )
            self.assertEqual(self.zamowienie.pozycje.count(), 1)
            pozycja = self.zamowienie.pozycje.first()
            self.assertEqual(pozycja.ksiazka, self.ksiazka)
            self.assertEqual(pozycja.ilosc, 1)
            self.assertEqual(float(pozycja.cena), float(self.ksiazka.cena))


from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ksiazka, Zakladka, ProfilUzytkownika

@receiver(post_save, sender=User)
def utworz_profil_uzytkownika(sender, instance, created, **kwargs):
    if created:
        from .models import ProfilUzytkownika
        ProfilUzytkownika.objects.create(user=instance)


@receiver(post_save, sender=Ksiazka)
def dodaj_zakladke_po_dodaniu_ksiazki(sender, instance, created, **kwargs):
    if created:

        Zakladka.objects.create( ksiazka=instance)


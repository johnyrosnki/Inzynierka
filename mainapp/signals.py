from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ksiazka,Zakladka

@receiver(post_save, sender=Ksiazka)
def dodaj_zakladke_po_dodaniu_ksiazki(sender, instance, created, **kwargs):
    if created:
        # Jeśli nowa książka została utworzona, dodaj zakładkę
        Zakladka.objects.create( ksiazka=instance)
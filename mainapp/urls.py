from django.urls import path
from . import views
from .views import dodaj_ksiazke
from .views import lista_ksiazek, ksiazki_wedlug_kategorii,dodaj_do_koszyka,wyswietl_koszyk,czysc_koszyk
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('ksiazki_wedlug_kategorii/<int:kategoria_id>/', ksiazki_wedlug_kategorii, name='ksiazki_wedlug_kategorii'),
    path('lista_ksiazek/', lista_ksiazek, name='lista_ksiazek'),
    path('dodaj_do_koszyka/<int:ksiazka_id>/', dodaj_do_koszyka, name='dodaj_do_koszyka'),
    path('koszyk/', wyswietl_koszyk, name='wyswietl_koszyk'),
    path('czysc_koszyk/', czysc_koszyk, name='czysc_koszyk')



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
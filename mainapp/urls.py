from django.urls import path
from . import views
from .views import dodaj_ksiazke
from .views import lista_ksiazek, ksiazki_wedlug_kategorii, dodaj_do_koszyka, wyswietl_koszyk, usun_z_koszyka, \
    rejestracja, logowanie, zwieksz_ilosc, zmniejsz_ilosc, ksiazka_szczegoly, WyszukiwarkaView, ksiazki_wedlug_autora, \
    wydawnictwo_szczegoly
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
                  path('', views.base, name='base'),
                  path('ksiazki_wedlug_kategorii/<int:kategoria_id>/', ksiazki_wedlug_kategorii,
                       name='ksiazki_wedlug_kategorii'),
                  path('lista_ksiazek/', lista_ksiazek, name='lista_ksiazek'),
                  path('dodaj_do_koszyka/<int:ksiazka_id>/', dodaj_do_koszyka, name='dodaj_do_koszyka'),
                  path('koszyk/', wyswietl_koszyk, name='wyswietl_koszyk'),
                  path('usun_z_koszyka/<int:ksiazka_id>/', usun_z_koszyka, name='usun_z_koszyka'),
                  path('rejestracja/', rejestracja, name='rejestracja'),
                  path('logowanie/', logowanie, name='logowanie'),
                  path('zwieksz_ilosc/<int:ksiazka_id>/', zwieksz_ilosc, name='zwieksz_ilosc'),
                  path('zmniejsz_ilosc/<int:ksiazka_id>/', zmniejsz_ilosc, name='zmniejsz_ilosc'),
                  path('wyloguj/', LogoutView.as_view(next_page='/'), name='wyloguj'),
                  path('ksiazka_szczegoly/<slug:slug>/', ksiazka_szczegoly, name='ksiazka_szczegoly'),
                  path('ksiazki_wedlug_autora/<slug:slug>/', ksiazki_wedlug_autora, name='ksiazki_wedlug_autora'),
                  path('wydawnictwo_szczegoly/<slug:slug>/', wydawnictwo_szczegoly, name='wydawnictwo_szczegoly'),
                  path('wyszukiwarka/', WyszukiwarkaView.as_view(), name='wyszukiwarka'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

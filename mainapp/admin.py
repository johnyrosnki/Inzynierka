from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Ksiazka, Kategoria, Autor, Wydawnictwo, PozycjaZamowienia, Zamowienie
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)
    exclude = ('slug',)
admin.site.register(Kategoria, KategoriaAdmin)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('imie', 'nazwisko')
    search_fields = ('imie','nazwisko')
    exclude = ('slug',)


admin.site.register(Autor,AutorAdmin)


class WydawnictwoAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)
    exclude = ('slug',)
admin.site.register(Wydawnictwo,WydawnictwoAdmin)
class KsiazkaAdmin(admin.ModelAdmin):
    list_display = ('tytul', 'cena', 'autor', 'opis', 'okladka','wydawnictwo')
    search_fields = ['tytul', 'autor__imie', 'autor__nazwisko','wydawnictwo']
    filter_horizontal = ('kategorie',)
    repopulated_fields = {'slug': ('tytul',)}
    exclude = ('slug',)

admin.site.register(Ksiazka, KsiazkaAdmin)
class UserAdmin(BaseUserAdmin):
    # Możesz dostosować wyświetlanie modelu User, ale pomiń odniesienia do ProfilUzytkownika
    pass

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)



@admin.register(PozycjaZamowienia)
class PozycjaZamowieniaAdmin(admin.ModelAdmin):
    list_display = ['zamowienie', 'ilosc',  'cena']
    list_filter = ['zamowienie']
    search_fields = ['zamowienie__id', 'tytul', 'autor']


@admin.register(Zamowienie)
class ZamowienieAdmin(admin.ModelAdmin):
    list_display = ['user', 'zaplacone','adres','kod_pocztowy','miasto','wojewodztwo']
    list_filter = ['zaplacone','adres']
    search_fields = ['user__username']




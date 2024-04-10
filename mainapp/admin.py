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
    list_display = ('tytul', 'cena', 'autor', 'opis', 'okladka','wydawnictwo','typ_okladki', 'rok_wydania')
    search_fields = ['tytul', 'autor__imie', 'autor__nazwisko','wydawnictwo','typ_okladki', 'rok_wydania']
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





class PozycjaZamowieniaInline(admin.TabularInline):
    model = PozycjaZamowienia
    extra = 0  # Domyślna liczba formularzy

@admin.register(Zamowienie)
class ZamowienieAdmin(admin.ModelAdmin):
    list_display = ['user', 'zaplacone', 'adres', 'kod_pocztowy', 'miasto', 'wojewodztwo','wyslano']
    list_filter = ['zaplacone', 'adres','wyslano']
    search_fields = ['user__username']
    inlines = [PozycjaZamowieniaInline]
    def tytul_ksiazki(self, obj):
        return obj.ksiazka.tytul
    tytul_ksiazki.short_description = "Tytuł książki"




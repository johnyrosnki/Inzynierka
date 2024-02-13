from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Ksiazka, Kategoria, Autor, Wydawnictwo, Zamowienie
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)
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






class ZamowienieAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'tytul', 'autor', 'ilosc', 'cena', 'zaplacone')  # Aktualizacja, aby wyświetlać czy zapłacone
    list_filter = ('zaplacone', 'user')  # Aktualizacja filtrów
    search_fields = ('tytul', 'autor', 'user__username')  # Aktualizacja pól wyszukiwania


admin.site.register(Zamowienie, ZamowienieAdmin)



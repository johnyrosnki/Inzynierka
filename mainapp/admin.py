from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Ksiazka,Kategoria,Autor,Wydawnictwo
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


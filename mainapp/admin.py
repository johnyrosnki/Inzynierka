from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Ksiazka,Kategoria,Autor
class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)
admin.site.register(Kategoria, KategoriaAdmin)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('imie', 'nazwisko')
    search_fields = ('imie','nazwisko')


admin.site.register(Autor,AutorAdmin)




class KsiazkaAdmin(admin.ModelAdmin):
    list_display = ('tytul', 'cena', 'autor', 'opis', 'okladka')
    search_fields = ['tytul', 'autor__imie', 'autor__nazwisko']
    filter_horizontal = ('kategorie',)
    repopulated_fields = {'slug': ('tytul',)}
    exclude = ('slug',)

admin.site.register(Ksiazka, KsiazkaAdmin)


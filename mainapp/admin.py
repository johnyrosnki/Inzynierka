from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Ksiazka,Kategoria
class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)

admin.site.register(Kategoria, KategoriaAdmin)
class KsiazkaAdmin(admin.ModelAdmin):
    list_display = ('tytul', 'cena', 'autor', 'opis', 'okladka')
    search_fields = ['tytul', 'autor']
    filter_horizontal = ('kategorie',)

admin.site.register(Ksiazka, KsiazkaAdmin)


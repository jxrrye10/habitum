from django.contrib import admin
from .models import Habito, Registro


@admin.register(Habito)
class HabitoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'creado')
    list_filter = ('usuario',)
    search_fields = ('nombre', 'usuario__username')


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('habito', 'fecha', 'completado')
    list_filter = ('completado', 'fecha', 'habito__usuario')
    search_fields = ('habito__nombre',)
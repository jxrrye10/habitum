from django.contrib import admin
from .models import Habito, Registro, Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre_personalizado')
    search_fields = ('usuario__username', 'nombre_personalizado')


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
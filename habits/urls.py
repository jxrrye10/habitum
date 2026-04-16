from django.urls import path
from . import views

urlpatterns = [
    # Autenticacion
    path('registro/', views.vista_registro, name='registro'),
    path('login/', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('marcar/<int:registro_id>/', views.marcar_habito, name='marcar_habito'),

    # Gestion de habitos
    path('habitos/nuevo/', views.crear_habito, name='crear_habito'),
    path('habitos/<int:habito_id>/editar/', views.editar_habito, name='editar_habito'),
    path('habitos/<int:habito_id>/eliminar/', views.eliminar_habito, name='eliminar_habito'),

    # Historial
    path('historial/', views.historial, name='historial'),

    # Perfil
    path('perfil/', views.editar_perfil, name='editar_perfil'),

    # Administracion (solo superusuario)
    path('administracion/usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('administracion/usuarios/<int:user_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('administracion/usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
]
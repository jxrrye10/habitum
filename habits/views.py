from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
import datetime

from .models import Habito, Registro, Perfil
from .forms import RegistroUsuarioForm, HabitoForm, PerfilForm


# ── DECORADOR ADMIN ───────────────────────────────────────────────────────────

def admin_required(view_func):
    """Decorador: solo superusuarios pueden acceder."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ── AUTENTICACION ─────────────────────────────────────────────────────────────

def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'Bienvenido, {usuario.username}.')
            return redirect('dashboard')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'habits/registro.html', {'form': form})


def vista_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contrasena incorrectos.')
    else:
        form = AuthenticationForm()
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    return render(request, 'habits/login.html', {'form': form})


def vista_logout(request):
    logout(request)
    return redirect('login')


# ── UTILIDADES ────────────────────────────────────────────────────────────────

def obtener_o_crear_registros_hoy(habitos, hoy):
    for habito in habitos:
        Registro.objects.get_or_create(
            habito=habito, fecha=hoy,
            defaults={'completado': False}
        )


def calcular_progreso(habitos, hoy):
    total = habitos.count()
    if total == 0:
        return 0, 0, 0
    completados = Registro.objects.filter(
        habito__in=habitos, fecha=hoy, completado=True
    ).count()
    porcentaje = int((completados / total) * 100)
    return total, completados, porcentaje


def calcular_racha(habitos):
    if not habitos.exists():
        return 0
    total = habitos.count()
    racha = 0
    fecha = datetime.date.today() - datetime.timedelta(days=1)
    while True:
        completados = Registro.objects.filter(
            habito__in=habitos, fecha=fecha, completado=True
        ).count()
        if completados == total:
            racha += 1
            fecha -= datetime.timedelta(days=1)
        else:
            break
        if racha > 3650:
            break
    return racha


def _datos_dashboard(usuario, hoy):
    """Calcula todos los datos del dashboard para un usuario dado."""
    habitos = Habito.objects.filter(usuario=usuario)
    obtener_o_crear_registros_hoy(habitos, hoy)
    registros_hoy = Registro.objects.filter(
        habito__in=habitos, fecha=hoy
    ).select_related('habito')
    total, completados, porcentaje = calcular_progreso(habitos, hoy)
    racha = calcular_racha(habitos)
    return {
        'registros_hoy': registros_hoy,
        'hoy': hoy,
        'total': total,
        'completados': completados,
        'porcentaje': porcentaje,
        'racha': racha,
    }


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    hoy = datetime.date.today()
    ctx = _datos_dashboard(request.user, hoy)
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        perfil = Perfil.objects.create(usuario=request.user)
    ctx['perfil'] = perfil
    return render(request, 'habits/dashboard.html', ctx)


@login_required
def marcar_habito(request, registro_id):
    registro = get_object_or_404(
        Registro, id=registro_id, habito__usuario=request.user
    )
    registro.completado = not registro.completado
    registro.save()
    return redirect('dashboard')


# ── GESTION DE HABITOS ────────────────────────────────────────────────────────

@login_required
def crear_habito(request):
    if request.method == 'POST':
        form = HabitoForm(request.POST)
        if form.is_valid():
            habito = form.save(commit=False)
            habito.usuario = request.user
            habito.save()
            messages.success(request, f'Habito "{habito.nombre}" creado.')
            return redirect('dashboard')
    else:
        form = HabitoForm()
    return render(request, 'habits/habito_form.html', {
        'form': form, 'titulo': 'Nuevo habito'
    })


@login_required
def editar_habito(request, habito_id):
    habito = get_object_or_404(Habito, id=habito_id, usuario=request.user)
    if request.method == 'POST':
        form = HabitoForm(request.POST, instance=habito)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habito actualizado.')
            return redirect('dashboard')
    else:
        form = HabitoForm(instance=habito)
    return render(request, 'habits/habito_form.html', {
        'form': form, 'titulo': 'Editar habito', 'habito': habito
    })


@login_required
def eliminar_habito(request, habito_id):
    habito = get_object_or_404(Habito, id=habito_id, usuario=request.user)
    if request.method == 'POST':
        nombre = habito.nombre
        habito.delete()
        messages.success(request, f'Habito "{nombre}" eliminado.')
        return redirect('dashboard')
    return render(request, 'habits/habito_confirmar_eliminar.html', {'habito': habito})


# ── HISTORIAL ─────────────────────────────────────────────────────────────────

@login_required
def historial(request):
    habitos = Habito.objects.filter(usuario=request.user)
    hoy = datetime.date.today()
    dias = []
    for i in range(1, 31):
        fecha = hoy - datetime.timedelta(days=i)
        registros = Registro.objects.filter(
            habito__in=habitos, fecha=fecha
        ).select_related('habito')
        total = habitos.count()
        completados_dia = registros.filter(completado=True).count()
        porcentaje_dia = int((completados_dia / total) * 100) if total > 0 else 0
        dias.append({
            'fecha': fecha,
            'registros': registros,
            'total': total,
            'completados': completados_dia,
            'porcentaje': porcentaje_dia,
        })
    return render(request, 'habits/historial.html', {'dias': dias})


# ── PERFIL DE USUARIO ─────────────────────────────────────────────────────────

@login_required
def editar_perfil(request):
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        perfil = Perfil.objects.create(usuario=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('editar_perfil')
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'habits/perfil.html', {'form': form, 'perfil': perfil})


# ── VISTAS DE ADMINISTRADOR ───────────────────────────────────────────────────

@admin_required
def lista_usuarios(request):
    usuarios = User.objects.all().select_related('perfil').order_by('-date_joined')
    datos = []
    hoy = datetime.date.today()
    for u in usuarios:
        habitos = Habito.objects.filter(usuario=u)
        total, completados, porcentaje = calcular_progreso(habitos, hoy)
        try:
            perfil = u.perfil
        except Perfil.DoesNotExist:
            perfil = Perfil.objects.create(usuario=u)
        datos.append({
            'usuario': u,
            'perfil': perfil,
            'total_habitos': habitos.count(),
            'completados_hoy': completados,
            'porcentaje_hoy': porcentaje,
        })
    return render(request, 'habits/admin_usuarios.html', {'datos': datos})


@admin_required
def detalle_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    try:
        perfil = usuario.perfil
    except Perfil.DoesNotExist:
        perfil = Perfil.objects.create(usuario=usuario)

    hoy = datetime.date.today()
    habitos = Habito.objects.filter(usuario=usuario)
    obtener_o_crear_registros_hoy(habitos, hoy)

    registros_hoy = Registro.objects.filter(
        habito__in=habitos, fecha=hoy
    ).select_related('habito')
    total, completados, porcentaje = calcular_progreso(habitos, hoy)
    racha = calcular_racha(habitos)

    # Historial de los ultimos 14 dias
    dias = []
    for i in range(1, 15):
        fecha = hoy - datetime.timedelta(days=i)
        regs = Registro.objects.filter(
            habito__in=habitos, fecha=fecha
        ).select_related('habito')
        t = habitos.count()
        c = regs.filter(completado=True).count()
        p = int((c / t) * 100) if t > 0 else 0
        dias.append({'fecha': fecha, 'registros': regs, 'total': t, 'completados': c, 'porcentaje': p})

    return render(request, 'habits/admin_usuario_detalle.html', {
        'usuario_obj': usuario,
        'perfil': perfil,
        'registros_hoy': registros_hoy,
        'hoy': hoy,
        'total': total,
        'completados': completados,
        'porcentaje': porcentaje,
        'racha': racha,
        'dias': dias,
    })


@admin_required
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta de administrador.')
        return redirect('lista_usuarios')
    if request.method == 'POST':
        nombre = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{nombre}" eliminado correctamente.')
        return redirect('lista_usuarios')
    try:
        perfil = usuario.perfil
    except Perfil.DoesNotExist:
        perfil = None
    return render(request, 'habits/admin_usuario_confirmar_eliminar.html', {
        'usuario_obj': usuario,
        'perfil': perfil,
    })
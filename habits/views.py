from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime

from .models import Habito, Registro
from .forms import RegistroUsuarioForm, HabitoForm


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


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    hoy = datetime.date.today()
    habitos = Habito.objects.filter(usuario=request.user)
    obtener_o_crear_registros_hoy(habitos, hoy)
    registros_hoy = Registro.objects.filter(
        habito__in=habitos, fecha=hoy
    ).select_related('habito')
    total, completados, porcentaje = calcular_progreso(habitos, hoy)
    racha = calcular_racha(habitos)
    return render(request, 'habits/dashboard.html', {
        'registros_hoy': registros_hoy,
        'hoy': hoy,
        'total': total,
        'completados': completados,
        'porcentaje': porcentaje,
        'racha': racha,
    })


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
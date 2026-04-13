from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Habito


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electronico')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''


class HabitoForm(forms.ModelForm):
    class Meta:
        model = Habito
        fields = ['nombre']
        labels = {'nombre': 'Nombre del habito'}
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Leer 30 minutos',
                'autofocus': True,
            })
        }
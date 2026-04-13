from django.db import models
from django.contrib.auth.models import User


class Habito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habitos')
    nombre = models.CharField(max_length=200)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado']
        verbose_name = 'Habito'
        verbose_name_plural = 'Habitos'

    def __str__(self):
        return f'{self.nombre} ({self.usuario.username})'


class Registro(models.Model):
    habito = models.ForeignKey(Habito, on_delete=models.CASCADE, related_name='registros')
    fecha = models.DateField()
    completado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habito', 'fecha')
        ordering = ['-fecha']
        verbose_name = 'Registro'
        verbose_name_plural = 'Registros'

    def __str__(self):
        estado = 'completado' if self.completado else 'pendiente'
        return f'{self.habito.nombre} - {self.fecha} ({estado})'
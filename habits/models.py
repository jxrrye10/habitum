from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nombre_personalizado = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'Perfil de {self.usuario.username}'

    def get_nombre(self):
        """Devuelve nombre personalizado o username como fallback."""
        return self.nombre_personalizado or self.usuario.username

    def get_foto_url(self):
        """Devuelve URL de foto o avatar generado por DiceBear."""
        if self.foto:
            return self.foto.url
        seed = self.usuario.username
        return f'https://api.dicebear.com/7.x/initials/svg?seed={seed}&backgroundColor=2d5016&textColor=ffffff&radius=50'


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
from django.db import models

#TODO: Creación de usuarios con Google


class Controlador(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del controlador")
    ultima_conexion = models.DateTimeField(auto_now=True, help_text="Última conexión con el controlador")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Controlador"
        verbose_name_plural = "Controladores"

class Casillero(models.Model):
    identificador = models.CharField(max_length=50, unique=True, help_text="Identificador único del casillero")
    email = models.EmailField(max_length=50, blank=True)
    controlador = models.ForeignKey(Controlador, on_delete=models.CASCADE, related_name="casilleros")
    ubicacion = models.CharField(max_length=100, blank=True, help_text="Ubicación física del casillero")
    abierto = models.BooleanField(default=False)
    clave = models.CharField(default="0000")

    def __str__(self):
        return f"{self.identificador} - {self.controlador.nombre}"

    class Meta:
        verbose_name = "Casillero"
        verbose_name_plural = "Casilleros"
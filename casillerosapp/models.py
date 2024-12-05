from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import timedelta

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Superuser', 'Superuser'),
        ('User', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    total_time_used = models.DurationField(default=timedelta())  # Tiempo total acumulado
    last_login_time = models.DateTimeField(null=True, blank=True)  # Último inicio de sesión

    # Ajustar los related_name para evitar conflictos
    groups = models.ManyToManyField(
        Group,
        related_name="user_group",  # Cambia el related_name para evitar conflictos
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="role_permisions",  # Cambia el related_name para evitar conflictos
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )


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
    _skip_signal = False

    def __str__(self):
        return f"{self.identificador} - {self.controlador.nombre}"

    class Meta:
        verbose_name = "Casillero"
        verbose_name_plural = "Casilleros"

class Logs(models.Model):
    TYPE_CHOICES = (
        ('Cambio_contraseña', 'Cambio de contraseña'),
        ('Apertura', 'Apertura de casillero'),
        ('Cierre', 'Cierre de casillero'),
        ('Error', 'Error de Apertura'),
    )
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    casillero = models.ForeignKey(Casillero, on_delete=models.CASCADE, related_name="logs")
    fecha = models.DateTimeField()
    mensaje = models.TextField()
    password= models.CharField(max_length=5, blank=True)


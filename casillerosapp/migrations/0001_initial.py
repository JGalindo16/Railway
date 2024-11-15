# Generated by Django 4.2.16 on 2024-11-10 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Controlador",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nombre",
                    models.CharField(
                        help_text="Nombre del controlador", max_length=100, unique=True
                    ),
                ),
                (
                    "ultima_conexion",
                    models.DateTimeField(
                        auto_now=True, help_text="Última conexión con el controlador"
                    ),
                ),
            ],
            options={
                "verbose_name": "Controlador",
                "verbose_name_plural": "Controladores",
            },
        ),
        migrations.CreateModel(
            name="Casillero",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "identificador",
                    models.CharField(
                        help_text="Identificador único del casillero",
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=50)),
                (
                    "ubicacion",
                    models.CharField(
                        blank=True,
                        help_text="Ubicación física del casillero",
                        max_length=100,
                    ),
                ),
                ("abierto", models.BooleanField(default=False)),
                ("clave", models.CharField(default="0000")),
                (
                    "controlador",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="casilleros",
                        to="casillerosapp.controlador",
                    ),
                ),
            ],
            options={
                "verbose_name": "Casillero",
                "verbose_name_plural": "Casilleros",
            },
        ),
    ]

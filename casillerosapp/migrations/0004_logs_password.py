# Generated by Django 4.2.16 on 2024-11-29 20:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("casillerosapp", "0003_alter_logs_fecha"),
    ]

    operations = [
        migrations.AddField(
            model_name="logs",
            name="password",
            field=models.CharField(blank=True, max_length=5),
        ),
    ]

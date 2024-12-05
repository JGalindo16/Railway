from django import template
from datetime import timedelta
from django.utils.timezone import localtime

register = template.Library()

@register.filter
def restar_horas(fecha, horas):
    if fecha:
        return localtime(fecha) - timedelta(hours=int(horas))
    return fecha
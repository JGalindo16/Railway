from django.contrib import admin
from casillerosapp.models import Controlador, Casillero, User, Logs


admin.site.register(Controlador)
admin.site.register(Casillero)
admin.site.register(User)
admin.site.register(Logs)


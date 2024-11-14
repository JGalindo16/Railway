from django.urls import path 
from casillerosapp.views import views
from casillerosapp.views.mqtt import mqtt_views
from casillerosapp.views.controladores import controladores_view

urlpatterns = [
    path("", views.home, name='home'),
    path("login/", views.login, name="login"),  
    path("logout/", views.logout, name='logout'),
    path('mqtt/', mqtt_views.mqtt_view, name='mqtt'),
    path('mqtt/messages/', mqtt_views.show_messages_view, name='show_messages_view'),
    path('lista_controladores', controladores_view.lista_controladores, name='lista_controladores'),
    path('<int:controlador_id>/', controladores_view.detalle_controlador, name='detalle_controlador'),
    path('actualizar_casillero_usuario/<int:casillero_id>/', controladores_view.actualizar_casillero_usuario, name='actualizar_casillero_usuario'),
    path('cargar_formulario_usuario/<int:casillero_id>/', controladores_view.cargar_formulario_usuario, name='cargar_formulario_usuario'),
]


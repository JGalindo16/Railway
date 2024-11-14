from django.shortcuts import render, get_object_or_404, redirect
from casillerosapp.models import Controlador, Casillero
from casillerosapp.forms import UsuarioCasilleroForm
from casillerosapp.choices import KEY_CHOICES
from django.contrib import messages
import paho.mqtt.client as mqtt
import ssl
import threading
from datetime import datetime, timedelta
import pytz
import json
import time
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives

# Configuración MQTT
client = mqtt.Client()
client.username_pw_set("admin", "admin")

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
client.tls_set_context(context)

# Diccionario para almacenar la última vez que se recibió un mensaje de cada controlador
last_message_time = {}

# Callback de conexión MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado exitosamente al broker MQTT")
        client.subscribe("test/topic")  # Tópico de estado de la ESP32
    else:
        print(f"Error al conectar: {rc}")

def send_status_email(casillero):
    email = casillero.email
    subject = "Confirmación de Casillero Actualizado"

    # Renderizar el contenido HTML con el template
    html_content = render_to_string('email/status_mail.html', {
        'casillero': casillero,
    })

    # Convertir el contenido HTML a texto plano
    text_content = strip_tags(html_content)

    # Configurar y enviar el correo
    email_message = EmailMultiAlternatives(
        subject,
        text_content,
        'grupo11.pds@gmail.com', 
        [email],
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send(fail_silently=False)


def on_message(client, userdata, msg):
    global last_message_time
    mensaje = json.loads(msg.payload.decode())

    nombre_controlador = mensaje.get("nombre", "No hay nombre")
    try:
        controlador = Controlador.objects.get(nombre=nombre_controlador)
    except Controlador.DoesNotExist:
        print(f"No se encontró un controlador con el nombre '{nombre_controlador}'")
        return

    timestamp_str = mensaje.get("timestamp", None)
    timezone = pytz.timezone('America/Santiago')
    timestamp = timezone.localize(datetime.fromisoformat(timestamp_str)) if timestamp_str else datetime.now(timezone)
    controlador.ultima_conexion = timestamp
    controlador.save()

    last_message_time[controlador.id] = timestamp

    for casillero_data in mensaje.get("casilleros", []):
        identificador = casillero_data["identificador"]
        estado_abierto = casillero_data["abierto"]

        try:
            casillero = Casillero.objects.get(identificador=identificador, controlador=controlador)
            if casillero.abierto != estado_abierto:
                send_status_email(casillero)
                casillero.abierto = estado_abierto
                casillero.save()
        except Casillero.DoesNotExist:
            print(f"No se encontró un casillero con el identificador '{identificador}' para el controlador '{controlador.nombre}'")


# Conectar al broker y mantener el bucle activo en un hilo separado
def connect_mqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print("conectando al broker")
        client.connect("2c0bd908f27d411fb30f8ea2ace36789.s1.eu.hivemq.cloud", 8883, 60)
        threading.Thread(target=client.loop_start).start()
    except Exception as e:
        print(f"Error conectando al broker: {e}")

connect_mqtt()

# Función para obtener el estado actual de la ESP32
def obtener_estado_controlador(controlador):
    if str(controlador.id) in last_message_time:
        last_timestamp = last_message_time[str(controlador.id)]
        if datetime.now(pytz.timezone('America/Santiago')) - last_timestamp < timedelta(minutes=3):
            return "Conectado", last_timestamp
    return "Desconectado", controlador.ultima_conexion


# Vista para la lista de controladores
def lista_controladores(request):
    controladores = Controlador.objects.all()
    for controlador in controladores:
        controlador.estado = obtener_estado_controlador(str(controlador.id))
    return render(request, 'controladores/lista_controladores.html', {'controladores': controladores})

def obtener_estado_controlador(controlador_id):
    timezone = pytz.timezone('America/Santiago')
    try:
        controlador = Controlador.objects.get(id=controlador_id)
    except Controlador.DoesNotExist:
        controlador = Controlador.objects.first()  # Utiliza el primer controlador si no se encuentra el ID
    
    ultima_conexion = controlador.ultima_conexion 

    # Calcular la diferencia entre el último timestamp y el tiempo actual
    if ultima_conexion:
        tiempo_actual = datetime.now(timezone)
        diferencia = tiempo_actual - ultima_conexion
        if diferencia <= timedelta(minutes=5):
            return "Conectado", tiempo_actual
    return "Desconectado", ultima_conexion


def detalle_controlador(request, controlador_id):
    controlador = get_object_or_404(Controlador, id=controlador_id)
    casilleros = controlador.casilleros.all()
    form_usuario = UsuarioCasilleroForm()

    # Enviar JSON completo al broker al hacer clic en actualizar
    if request.method == 'POST' and 'actualizar_estado' in request.POST:
        enviar_json_controlador(controlador)
        messages.success(request, f"Estado de {controlador.nombre} enviado al broker MQTT.")
    
    # Actualizar estado de conexión
    controlador.estado, controlador.ultima_conexion = obtener_estado_controlador(controlador.id)

    # Guardar la última conexión en la base de datos si está conectado
    if controlador.estado == "Conectado":
        controlador.save()

    ultima_conexion= controlador.ultima_conexion - timedelta(hours=3)
    
    return render(request, 'controladores/detalle_controlador.html', {
        'controlador': controlador,
        'casilleros': casilleros,
        'form_usuario': form_usuario,
        'estado_conexion': controlador.estado,
        'ultima_conexion': ultima_conexion
    })



# Vista para actualizar la clave del casillero
def actualizar_casillero_usuario(request, casillero_id):
    casillero = get_object_or_404(Casillero, id=casillero_id)
    if request.method == 'POST':
        form_usuario = UsuarioCasilleroForm(request.POST)
        if form_usuario.is_valid():
            casillero.email = form_usuario.cleaned_data['usuario_email']
            nueva_clave = "".join([request.POST.get(f'clave{i}') for i in "1234"])
            casillero.clave = nueva_clave
            casillero.save()
            
            # Enviar JSON completo al broker tras actualizar la clave
            enviar_json_controlador(casillero.controlador)
            messages.success(request, f"Clave del casillero {casillero.identificador} actualizada y enviada a ESP32.")
            
            return redirect('detalle_controlador', controlador_id=casillero.controlador.id)
    else:
        form_usuario = UsuarioCasilleroForm(initial={'usuario_email': casillero.email})

    return render(request, 'controladores/modal_formulario_usuario.html', {
        'form_usuario': form_usuario,
        'casillero': casillero,
        'KEY_CHOICES': KEY_CHOICES,
    })

# Vista para cargar el formulario del casillero
def cargar_formulario_usuario(request, casillero_id):
    casillero = get_object_or_404(Casillero, id=casillero_id)
    form_usuario = UsuarioCasilleroForm(initial={'usuario_email': casillero.email})
    return render(request, 'controladores/modal_formulario_usuario.html', {
        'form_usuario': form_usuario,
        'casillero': casillero
    })

# Función para enviar JSON completo del controlador y sus casilleros al broker
def enviar_json_controlador(controlador):
    casilleros_data = [
        {
            'identificador': casillero.identificador,
            'abierto': casillero.abierto,
            'clave': casillero.clave
        }
        for casillero in controlador.casilleros.all()
    ]
    message = {
        'nombre': controlador.nombre,
        'modelo': 'https://modelo.de.ejemplo.com',
        'timestamp': datetime.now(pytz.timezone('America/Santiago')).isoformat(),
        'numero_casilleros': controlador.casilleros.count(),
        'casilleros': casilleros_data
    }
    time.sleep(2)  # Espera un poco para permitir el callback
    client.publish("esp32/status",  json.dumps(message))

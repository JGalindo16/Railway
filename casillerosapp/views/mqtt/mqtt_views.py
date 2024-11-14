from django.shortcuts import render, redirect
from django.contrib import messages
import paho.mqtt.client as mqtt
import ssl
import threading
import time
from datetime import datetime
import pytz  # Importar pytz para manejar zonas horarias
from django.contrib.auth.decorators import login_required

# Variable global para almacenar mensajes recibidos
received_messages = []

# Callbacks de MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Callback on_connect ejecutado con rc={rc}")
    if rc == 0:
        print("Conectado exitosamente al broker MQTT")
        # Suscribirse al tópico de la ESP32
        client.subscribe("test/topic")
    else:
        print(f"Error al conectar con el código {rc}")

def on_message(client, userdata, msg):
    global received_messages
    # Obtener la hora actual en la zona horaria de Santiago de Chile
    timezone = pytz.timezone('America/Santiago')
    timestamp = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"[{timestamp}] {msg.topic} - {msg.payload.decode()}"
    received_messages.append(message)
    print(message)

@login_required(login_url='/login')
def mqtt_view(request):
    if request.method == "POST":
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        
        client.username_pw_set("admin", "admin")  # Ingresa tus credenciales reales
        
        # Configurar SSL/TLS
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # Desactivar la verificación de certificados para pruebas

        client.tls_set_context(context)
        
        try:
            print("Intentando conectar al broker MQTT con TLS...")
            rc = client.connect("2c0bd908f27d411fb30f8ea2ace36789.s1.eu.hivemq.cloud", 8883, 60)
            print(f"Código de retorno de la conexión: {rc}")

            # Usa un subproceso para mantener el bucle activo
            thread = threading.Thread(target=client.loop_forever)
            thread.start()

            time.sleep(2)  # Espera un poco para permitir el callback
            client.publish("django/topic", "Mensaje desde Django")  # Publicar un mensaje en django/topic

            messages.success(request, "Mensaje enviado a django/topic y conectado al broker MQTT.")
        except Exception as e:
            print(f"Error al conectar: {e}")
            messages.error(request, f"Error al conectar al broker o enviar el mensaje: {e}")
        
        return redirect('show_messages_view')
    return render(request, 'mqtt/mqtt_template.html')

@login_required(login_url='/login')
def show_messages_view(request):
    global received_messages
    return render(request, 'mqtt/show_messages.html', {'messages': received_messages})

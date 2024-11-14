from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models.signals import post_save
from casillerosapp.models import Casillero

@receiver(user_signed_up)
def populate_user_profile(sender, request, user, sociallogin=None, **kwargs):
    if sociallogin:
        extra_data = sociallogin.account.extra_data
        user.first_name = extra_data.get('given_name', '')
        user.last_name = extra_data.get('family_name', '')
        user.save()

@receiver(post_save, sender=Casillero)
def send_confirmation_email(sender, instance, created, **kwargs):
    subject = "Confirmación de Casillero Actualizado"
    casillero = instance  # El objeto 'casillero' guardado

    # Verificamos si el casillero tiene un email asociado
    if not casillero.email:
        return  # No enviar correo si el email no está definido

    # Renderizamos el contenido HTML con el template
    html_content = render_to_string('email/confirmation_email.html', {
        'casillero': casillero,
    })

    # Convertimos el contenido HTML a texto plano (opcional)
    text_content = strip_tags(html_content)

    # Enviamos el correo utilizando EmailMultiAlternatives
    email = EmailMultiAlternatives(
        subject,
        text_content,
        'grupo11.pds@gmail.com',  # Correo desde el que se envía
        [casillero.email],  # Se usa el email asociado al casillero
    )

    # Adjuntamos la versión HTML
    email.attach_alternative(html_content, "text/html")

    # Enviamos el correo
    email.send(fail_silently=False)



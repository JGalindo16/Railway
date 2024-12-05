from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from casillerosapp.models import Casillero, Logs
from django.db.models import Count
from datetime import timedelta
from django.utils.timezone import now
from django.http import JsonResponse
from django.db.models import Q, F
from django.core.paginator import Paginator
from casillerosapp.models import User


def login(request): 
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "base/login.html")

def logout(request):
    # Cierra la sesión del usuario
    django_logout(request)
    print("Logout realizado correctamente")
    return redirect("login")

@login_required(login_url='/login')
def home(request):
    user = request.user

    # Información básica del usuario
    name = user.first_name.capitalize() if user.first_name else ''
    last_name = user.last_name.capitalize() if user.last_name else ''

    # Calcula el tiempo desde el último inicio de sesión
    if user.last_login_time:
        elapsed_time = now() - user.last_login_time
        user.total_time_used += elapsed_time
        user.last_login_time = now()
        user.save()

    # Formatear el tiempo total de uso en formato HH:MM:SS
    total_seconds = int(user.total_time_used.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_time_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"

    if user.role == "Superuser":
        # Obtener usuarios con el rol "User"
        usuarios = User.objects.filter(role="User")

        # Determinar el rango de días para las estadísticas (por defecto 7 días)
        days = int(request.GET.get('days', 7))
        start_date = now() - timedelta(days=days)

        # Preparar estadísticas de usuarios
        usuarios_data = []
        for usuario in usuarios:
            casillero_count = Casillero.objects.filter(email=usuario.email).count()
            casillero_ids = Casillero.objects.filter(email=usuario.email).values_list('id', flat=True)
            interactions = Logs.objects.filter(casillero_id__in=casillero_ids, fecha__gte=start_date).count()

            # Formatear tiempo de uso
            total_seconds = int(usuario.total_time_used.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            total_time_formatted_user = f"{hours:02}:{minutes:02}:{seconds:02}"

            usuarios_data.append({
                'first_name': usuario.first_name.split()[0].capitalize(),
                'last_name': usuario.last_name.split()[0].capitalize(),
                'casillero_count': casillero_count,
                'total_time_formatted': total_time_formatted_user,
                'interactions': interactions,
            })

        # Paginación
        paginator = Paginator(usuarios_data, 5)  # 10 usuarios por página
        page_number = request.GET.get('page', 1)
        usuarios_page = paginator.get_page(page_number)

        # Datos para el gráfico de radar
        casillero_logs = Logs.objects.filter(fecha__gte=start_date).values('casillero__identificador').annotate(
            total_interactions=Count('id')
        )
        radar_labels = [log['casillero__identificador'] for log in casillero_logs]
        radar_data = [log['total_interactions'] for log in casillero_logs]

        context = {
            'name': name,
            'last_name': last_name,
            'role': user.role,
            'usuarios': usuarios_page,  # Datos paginados
            'radar_labels': radar_labels,
            'radar_data': radar_data,
            'days': days,
        }
    else:
        # Dashboard del usuario
        casilleros = Casillero.objects.filter(email=user.email)

        # Tipos de logs esperados
        TIPOS_LOGS = ["Apertura", "Cierre", "Cambio_contraseña"]

        # Por defecto, mostrar estadísticas de los últimos 7 días
        start_date = now() - timedelta(days=7)
        log_stats = Logs.objects.filter(casillero__in=casilleros, fecha__gte=start_date).values('type').annotate(count=Count('id'))

        log_counts = {tipo: 0 for tipo in TIPOS_LOGS}
        for stat in log_stats:
            log_counts[stat['type']] = stat['count']

        chart_labels = list(log_counts.keys())
        chart_data = list(log_counts.values())

        context = {
            'name': name,
            'last_name': last_name,
            'role': user.role,
            'casilleros': casilleros,
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'total_time_used': total_time_formatted,
        }

    return render(request, "base/home.html", context)


@login_required(login_url='/login')
def get_logs_statistics(request):
    user = request.user
    days = int(request.GET.get('days', 7))  # Número de días (por defecto: 7)
    start_date = now() - timedelta(days=days)

    if user.role == "Superuser":
        # Superusuario: Estadísticas generales de logs
        casillero_logs = Logs.objects.filter(fecha__gte=start_date).values('casillero__identificador').annotate(
            total_interactions=Count('id')
        )
        labels = [log['casillero__identificador'] for log in casillero_logs]
        data = [log['total_interactions'] for log in casillero_logs]
    else:
        # Usuario normal: Logs específicos de sus casilleros
        casilleros = Casillero.objects.filter(email=user.email)
        log_stats = Logs.objects.filter(casillero__in=casilleros, fecha__gte=start_date).values('type').annotate(count=Count('id'))

        TIPOS_LOGS = ["Apertura", "Cierre", "Cambio_contraseña"]
        log_counts = {tipo: 0 for tipo in TIPOS_LOGS}
        for stat in log_stats:
            log_counts[stat['type']] = stat['count']

        labels = list(log_counts.keys())
        data = list(log_counts.values())

    return JsonResponse({
        'labels': labels,
        'data': data,
    })


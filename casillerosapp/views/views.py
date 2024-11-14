from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required


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

    name = user.first_name.split()[0].capitalize() if user.first_name else ''
    last_name = user.last_name.split()[0].capitalize() if user.last_name else ''

    context = {
        'name': name,
        'last_name': last_name,
    }

    return render(request, "base/home.html", context)


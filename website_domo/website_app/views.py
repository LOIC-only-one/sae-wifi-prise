from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .mqtt_lib_sae import MqttConnexion
import threading
import logging
from django.contrib.auth.decorators import login_required


def user_login(request):
    """
    Fonction de gestion et parsage des élement de login
    
    --> Provient de la DOC django
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Identifiants invalides.'})
    return render(request, 'login.html')

def user_logout(request):
    """
    Fonction de gestion de la déconnexion d'un utilisateur
    
    --> Provient de la DOC django
    """
    logout(request)
    return redirect('login')

#############################################################
#############################################################

logging.basicConfig(level=logging.INFO)
mqtt_connexion = MqttConnexion()

def run_mqtt():
    """Fonction pour gérer la connexion MQTT dans un thread séparé."""
    mqtt_connexion.handle_connexion()

threading.Thread(target=run_mqtt, daemon=True).start()

@login_required(login_url='/login/')
def home(request):
    """Vue d'acceuil gestion de la température et des lumières avec MQTT"""
    if request.method == "POST":
        action = request.POST.get('action')
        if action:
            mqtt_connexion.handle_light(action)
    
    temp = mqtt_connexion.get_temp()

    return render(request, "index.html", {"temp": temp})

#############################################################
#############################################################
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .mqtt_lib_sae import MqttConnexion
import threading
import logging
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import Prise1ModelForm
from .models import PlageHoraire
from datetime import time


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

#logging.basicConfig(level=logging.INFO)
mqtt_connexion = MqttConnexion()

def run_mqtt():
    """Fonction pour gérer la connexion MQTT dans un thread séparé."""
    mqtt_connexion.handle_connexion()

threading.Thread(target=run_mqtt, daemon=True).start()

@login_required(login_url='/login/')
def home(request):
    """Vue d'acceuil gestion de la température et des lumières avec MQTT"""
    
    now = timezone.now().strftime("%H:%M:%S")
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action:
            mqtt_connexion.handle_light(action)
    
    temp = mqtt_connexion.get_temp()

    return render(request, "index.html", {"temp": temp, "time": now,})

from django.utils import timezone


@login_required(login_url='/login/')
def plage_horaire(request):
    """Vue de la page gestion des plages horaires..."""
    
    now = timezone.now().time()
    form1 = Prise1ModelForm()

    if request.method == 'POST':
        form1 = Prise1ModelForm(request.POST)
         
        if form1.is_valid():
            choice = form1.cleaned_data["led"]
            nom = form1.cleaned_data["nom_plage"]
            heure_fin = form1.cleaned_data["heure_fin"]
            heure_debut = form1.cleaned_data["heure_debut"] 
            action = form1.cleaned_data["actions"]
            
            PlageHoraire.objects.create(
                led=choice,
                nom_plage=nom,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                actions=action
            )
            
            if now < heure_fin and now > heure_debut:
                action_command = f"lumiere{choice[-1]}_{action}"
                mqtt_connexion.handle_light(action_command)            
            return redirect('plage_horaire')
        
    plage_objects = PlageHoraire.objects.all()
    return render(request, 'plage_horaires.html', {'form1': form1, 'plage_objects': plage_objects})




def plage_modifier(request, id):
    plage = get_object_or_404(PlageHoraire, pk=id)  # Utilisation du modèle
    if request.method == "POST":
        form = Prise1ModelForm(request.POST, instance=plage)  # Utilisation du ModelForm
        if form.is_valid():
            form.save()
            return redirect('plage_horaire')
    else:
        form = Prise1ModelForm(instance=plage)
    return render(request, 'plage_modifieur.html', {'form': form})

def plage_delete(request, id):
    obj = get_object_or_404(PlageHoraire, pk=id)  # Utilisation du modèle ici, pas du formulaire
    obj.delete()
    return redirect('plage_horaire')  # Redirection après la suppression

#############################################################
#############################################################
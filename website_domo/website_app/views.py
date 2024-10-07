import logging
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .mqtt_lib_sae import MqttConnexion
import threading
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import Prise1ModelForm
from .models import PlageHoraire
import pytz
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mqtt_connexion = MqttConnexion()
paris_tz = pytz.timezone('Europe/Paris')

light_states = {
    "lumiere1_status": "off",
    "lumiere2_status": "off"
}
alerte_state = {
    "temp": None,
}

def run_mqtt():
    mqtt_connexion.handle_connexion()

threading.Thread(target=run_mqtt, daemon=True).start()

def alerte_temp():
    topic = "sae301/temperature/status"
    while True:
        msg = mqtt_connexion.souscription(topic=topic)
        alerte_state["temp"] = "Une surchauffe est en cours..." if msg else None
        time.sleep(5)

threading.Thread(target=alerte_temp, daemon=True).start()

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"Utilisateur {username} connecté avec succès.")
            return redirect('home')
        else:
            logger.warning(f"Tentative de connexion échouée pour le nom d'utilisateur : {username}")
            return render(request, 'login.html', {'error': 'Identifiants invalides.'})
    return render(request, 'login.html')

def user_logout(request):
    logger.info("Utilisateur déconnecté.")
    logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def home(request):
    now = timezone.localtime(timezone.now()).strftime("%H:%M:%S")
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action:
            mqtt_connexion.handle_light(action)
            logger.info(f"Action effectuée : {action}")
            if action == "lumiere1_on":
                light_states["lumiere1_status"] = "on"
            elif action == "lumiere1_off":
                light_states["lumiere1_status"] = "off"
            elif action == "lumiere2_on":
                light_states["lumiere2_status"] = "on"
            elif action == "lumiere2_off":
                light_states["lumiere2_status"] = "off"
            elif action == "all_on":
                light_states["lumiere1_status"] = "on"
                light_states["lumiere2_status"] = "on"
            elif action == "all_off":
                light_states["lumiere1_status"] = "off"
                light_states["lumiere2_status"] = "off"
    
    temp = mqtt_connexion.get_temp()
    light_status = get_light_status()

    context = {
        "temp": temp,
        "time": now,
        "lumiere1_status": light_status["lumiere1_status"],
        "lumiere2_status": light_status["lumiere2_status"],
        "alerte": alerte_state["temp"]
    }

    return render(request, "index.html", context)

@login_required(login_url='/login/')
def plage_horaire(request):
    form1 = Prise1ModelForm()
    plages = PlageHoraire.objects.all()

    if request.method == 'POST':
        form1 = Prise1ModelForm(request.POST)
         
        if form1.is_valid():
            choice = form1.cleaned_data["led"]
            nom = form1.cleaned_data["nom_plage"]
            heure_debut = form1.cleaned_data["heure_debut"]
            heure_fin = form1.cleaned_data["heure_fin"]
            action = form1.cleaned_data["actions"]

            PlageHoraire.objects.create(
                led=choice,
                nom_plage=nom,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                actions=action
            )
            logger.info(f"Nouveau créneau horaire créé : {nom} de {heure_debut} à {heure_fin} avec l'action {action}")
            return redirect('plage_horaire')

    return render(request, 'plage_horaires.html', {
        'form1': form1,
        'plages': plages,
    })

def check_time(mqtt_connexion):
    led1_on = False
    led2_on = False

    while True:
        now = timezone.localtime(timezone.now(), paris_tz).time()
        plages = PlageHoraire.objects.all()

        for plage in plages:
            heure_debut = plage.heure_debut
            heure_fin = plage.heure_fin
            logger.info(f"Plage trouvée : {plage}")
            if heure_debut <= now < heure_fin:
                if plage.actions == "allumer":
                    if plage.led == "LED1" or plage.led == "ALL":
                        if not led1_on:
                            led1_on = True
                            mqtt_connexion.publication("sae301/led", "LED_ON")
                            light_states["lumiere1_status"] = "on"
                            logger.info(f"LED1 allumée par le planning : {plage.nom_plage}")
                    if plage.led == "LED2" or plage.led == "ALL":
                        if not led2_on:
                            led2_on = True
                            mqtt_connexion.publication("sae301_2/led", "LED_ON")
                            light_states["lumiere2_status"] = "on"
                            logger.info(f"LED2 allumée par le planning : {plage.nom_plage}")

                elif plage.actions == "eteindre":
                    if plage.led == "LED1" or plage.led == "ALL":
                        if led1_on:
                            led1_on = False
                            mqtt_connexion.publication("sae301/led", "LED_OFF")
                            light_states["lumiere1_status"] = "off"
                            logger.info(f"LED1 éteinte par le planning : {plage.nom_plage}")
                    if plage.led == "LED2" or plage.led == "ALL":
                        if led2_on:
                            led2_on = False
                            mqtt_connexion.publication("sae301_2/led", "LED_OFF")
                            light_states["lumiere2_status"] = "off"
                            logger.info(f"LED2 éteinte par le planning : {plage.nom_plage}")

            else:
                if plage.actions == "allumer":
                    if plage.led == "LED1" or plage.led == "ALL":
                        if led1_on:
                            led1_on = False
                            mqtt_connexion.publication("sae301/led", "LED_OFF")
                            light_states["lumiere1_status"] = "off"
                            logger.info(f"LED1 éteinte en dehors du planning : {plage.nom_plage}")
                    if plage.led == "LED2" or plage.led == "ALL":
                        if led2_on:
                            led2_on = False
                            mqtt_connexion.publication("sae301_2/led", "LED_OFF")
                            light_states["lumiere2_status"] = "off"
                            logger.info(f"LED2 éteinte en dehors du planning : {plage.nom_plage}")

                elif plage.actions == "eteindre":
                    if plage.led == "LED1" or plage.led == "ALL":
                        if not led1_on:
                            led1_on = True
                            mqtt_connexion.publication("sae301/led", "LED_ON")
                            light_states["lumiere1_status"] = "on"
                            logger.info(f"LED1 allumée en dehors du planning : {plage.nom_plage}")
                    if plage.led == "LED2" or plage.led == "ALL":
                        if not led2_on:
                            led2_on = True
                            mqtt_connexion.publication("sae301_2/led", "LED_ON")
                            light_states["lumiere2_status"] = "on"
                            logger.info(f"LED2 allumée en dehors du planning : {plage.nom_plage}")

        time.sleep(5)

threading.Thread(target=check_time, args=(mqtt_connexion,), daemon=True).start()

def get_light_status():
    return {
        "lumiere1_status": light_states["lumiere1_status"],
        "lumiere2_status": light_states["lumiere2_status"],
    }

def plage_modifier(request, id):
    plage = get_object_or_404(PlageHoraire, pk=id)
    if request.method == "POST":
        form = Prise1ModelForm(request.POST, instance=plage)
        if form.is_valid():
            form.save()
            logger.info(f"Créneau horaire {plage.nom_plage} modifié.")
            return redirect('plage_horaire')
    else:
        form = Prise1ModelForm(instance=plage)
    return render(request, 'plage_modifier.html', {'form': form, 'plage': plage})

def plage_delete(request, id):
    plage = get_object_or_404(PlageHoraire, pk=id)
    plage.delete()
    logger.info(f"Créneau horaire {plage.nom_plage} supprimé.")
    return redirect('plage_horaire')

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .mqtt_lib_sae import MqttConnexion
import threading
import logging
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import Prise1ModelForm
from .models import PlageHoraire
import pytz
import time

logging.basicConfig(level=logging.DEBUG)
mqtt_connexion = MqttConnexion()
paris_tz = pytz.timezone('Europe/Paris')

light_states = {
    "lumiere1_status": "off",
    "lumiere2_status": "off"
}
alerte_state = {
    "temp" : None,
}

def run_mqtt():
    """Permet de lancer une connexion mqtt à l'aide de la lib mqtt_lib_sae.py."""
    mqtt_connexion.handle_connexion()
threading.Thread(target=run_mqtt, daemon=True).start()

def alerte_temp():
    """Permet de vérifier et de gérer en continu une alerte de température ou non."""
    topic = "sae301/temperature/status"
    while True:
        msg = mqtt_connexion.souscription(topic=topic)
        if msg is not None and msg.topic == topic:
            if msg.payload:
                message = str(msg.payload.decode())
                if message == "Température élevée":
                    alerte_state["temp"] = "Une surchauffe est en cours..."
                else:
                    alerte_state["temp"] = None
        time.sleep(1)

threading.Thread(target=alerte_temp, daemon=True).start()

def user_login(request):
    """Vue de connexion pour un utilisateur déja créé au préalable."""
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
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def home(request):
    now = timezone.localtime(timezone.now()).strftime("%H:%M:%S")
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action:
            mqtt_connexion.handle_light(action)
            
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
    }

    return render(request, "index.html", context)

@login_required(login_url='/login/')
def plage_horaire(request):
    form1 = Prise1ModelForm()
    plages = PlageHoraire.objects.all()
    logging.debug(f"Plages horaires récupérées: {plages}")

    if request.method == 'POST':
        form1 = Prise1ModelForm(request.POST)
        logging.debug(f"Données POST reçues: {request.POST}")
         
        if form1.is_valid():
            choice = form1.cleaned_data["led"]
            nom = form1.cleaned_data["nom_plage"]
            heure_debut = form1.cleaned_data["heure_debut"]
            heure_fin = form1.cleaned_data["heure_fin"]
            action = form1.cleaned_data["actions"]

            plage_horaire = PlageHoraire.objects.create(
                led=choice,
                nom_plage=nom,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                actions=action
            )
            logging.info(f"Plage horaire créée: {plage_horaire}")

            return redirect('plage_horaire')

    return render(request, 'plage_horaires.html', {
        'form1': form1,
        'plages': plages,
    })


def check_time(mqtt_connexion):
    """Permet de vérifier si l'heure actuelle est dans une plage horaire

    :param mqtt_connexion: Connexion au broket MQTT
    :type mqtt_connexion: None 
    """
    led1_on = False
    led2_on = False

    while True:
        now = timezone.localtime(timezone.now(), paris_tz).strftime("%H:%M")
        logging.debug(f"Heure actuelle: {now}")
        plages = PlageHoraire.objects.all()
        last_led1_state = led1_on
        last_led2_state = led2_on
        led1_on = False
        led2_on = False

        for plage in plages:
            heure_debut = plage.heure_debut.strftime("%H:%M")
            heure_fin = plage.heure_fin.strftime("%H:%M")
            logging.debug(f"Vérification de la plage: début = {heure_debut}, fin = {heure_fin}, action = {plage.actions}, LED = {plage.led}")

            if heure_debut <= now < heure_fin:
                if plage.actions == "allumer":
                    if plage.led == "LED1":
                        led1_on = True
                        logging.info(f"Action {plage.actions} pour la LED {plage.led} à {now}. LED {plage.led} sera allumée.")
                    elif plage.led == "LED2":
                        led2_on = True
                        logging.info(f"Action {plage.actions} pour la LED {plage.led} à {now}. LED {plage.led} sera allumée.")
                    elif plage.lde == "ALL":
                        led1_on,led2_on = True
                else:
                    if plage.actions == "eteindre":
                        if plage.led == "LED1":
                            led1_on = False
                        elif plage.led == "LED2":
                            led2_on = False
                        elif plage.led == "ALL":
                            led1_on,led2_on = False

        if led1_on and not last_led1_state:
            mqtt_connexion.publication("sae301/led", "LED_ON")
            logging.info("LED1 est allumée.")
            light_states["lumiere1_status"] = "on"
        elif not led1_on and last_led1_state:
            mqtt_connexion.publication("sae301/led", "LED_OFF")
            logging.info("LED1 est éteinte.")
            light_states["lumiere1_status"] = "off"

        if led2_on and not last_led2_state:
            mqtt_connexion.publication("sae301_2/led", "LED_ON")
            logging.info("LED2 est allumée.")
            light_states["lumiere2_status"] = "on"
        elif not led2_on and last_led2_state:
            mqtt_connexion.publication("sae301_2/led", "LED_OFF")
            logging.info("LED2 est éteinte.")
            light_states["lumiere2_status"] = "off"
        time.sleep(15)
threading.Thread(target=check_time, args=(mqtt_connexion,), daemon=True).start()

def get_light_status():
    """Permet de retourner le status des LEDS

    :return: Un context qui contient les etats des lumieres
    :rtype: dict
    """
    return {
        "lumiere1_status": light_states["lumiere1_status"],
        "lumiere2_status": light_states["lumiere2_status"],
    }

# Partie du CRUD concernant les plages horaires
def plage_modifier(request, id):
    plage = get_object_or_404(PlageHoraire, pk=id)
    if request.method == "POST":
        form = Prise1ModelForm(request.POST, instance=plage)
        if form.is_valid():
            form.save()
            return redirect('plage_horaire')
    else:
        form = Prise1ModelForm(instance=plage)
    return render(request, 'plage_modifieur.html', {'form': form})


def plage_delete(request, id):
    obj = get_object_or_404(PlageHoraire, pk=id)
    obj.delete()
    return redirect('plage_horaire')

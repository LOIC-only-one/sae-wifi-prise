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

def run_mqtt():
    mqtt_connexion.handle_connexion()

threading.Thread(target=run_mqtt, daemon=True).start()

def user_login(request):
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

paris_tz = pytz.timezone('Europe/Paris')

@login_required(login_url='/login/')
def home(request):
    now = timezone.localtime(timezone.now(), paris_tz).strftime("%H:%M:%S")
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action:
            mqtt_connexion.handle_light(action)
    
    temp = mqtt_connexion.get_temp()

    return render(request, "index.html", {"temp": temp, "time": now})

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

    return render(request, 'plage_horaires.html', {'form1': form1, 'plages': plages})

def check_time(mqtt_connexion):
    while True:
        now = timezone.localtime(timezone.now(), paris_tz).strftime("%H:%M")
        logging.debug(f"Heure actuelle: {now}")

        plages = PlageHoraire.objects.all()
        led1_on = False
        led2_on = False

        for plage in plages:
            heure_debut = plage.heure_debut.strftime("%H:%M")
            heure_fin = plage.heure_fin.strftime("%H:%M")
            logging.debug(f"Vérification de la plage: début = {heure_debut}, fin = {heure_fin}, action = {plage.actions}, LED = {plage.led}")

            if heure_debut <= now < heure_fin:
                logging.debug(f"L'heure actuelle {now} est dans la plage horaire ({heure_debut}, {heure_fin}).")
                if plage.actions == "allumer":
                    if plage.led == "LED1":
                        led1_on = True
                        logging.info(f"Action {plage.actions} pour la LED {plage.led} à {now}. LED {plage.led} sera allumée.")
                    elif plage.led == "LED2":
                        led2_on = True
                        logging.info(f"Action {plage.actions} pour la LED {plage.led} à {now}. LED {plage.led} sera allumée.")

            ### On peut ajouter ici la regle des deux led
        if led1_on:
            mqtt_connexion.publication("sae301/led", "LED_ON")
            logging.info("LED1 est allumée.")
        else:
            mqtt_connexion.publication("sae301/led", "LED_OFF")
            logging.info("LED1 est éteinte.")

        if led2_on:
            mqtt_connexion.publication("sae301_2/led", "LED_ON")
            logging.info("LED2 est allumée.")
        else:
            mqtt_connexion.publication("sae301_2/led", "LED_OFF")
            logging.info("LED2 est éteinte.")

        time.sleep(15)

threading.Thread(target=check_time, args=(mqtt_connexion,), daemon=True).start()

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

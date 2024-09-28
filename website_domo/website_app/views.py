from django.http import HttpResponse
from django.shortcuts import render
from .mqtt_lib_sae import MqttConnexion

def home(request):
    connexion = MqttConnexion(topic="sae301/led/status")
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action:
            connexion.handle_light(action)
    
    temp = connexion.get_temp()
    
    return render(request, "index.html", {"temp": temp})

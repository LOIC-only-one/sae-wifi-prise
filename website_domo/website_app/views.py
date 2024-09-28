from django.http import HttpResponse
from django.shortcuts import render
from .mqtt_lib_sae import MqttConnexion

def home(request):
    connexion = MqttConnexion()

    if request.method == "POST":
        action = request.POST.get('action')
        if action:
            connexion.handle_light(action)

    temp_topic = 'sae301/temperature'
    connexion.get_temp(temp_topic)
    temp = connexion.client.loop()

    return render(request, "index.html", {"temp": temp})

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from .models import *
import csv
from mqtt_lib_sae import MqttConnexion

def home(request):
    return HttpResponse("Bienvenue sur la page d'accueil de votre site !")

from django.db import models

class PlageHoraire(models.Model):
    LED_CHOICES = [
        ('LED1', "LED 1"),
        ('LED2', "LED 2"),
        ('ALL', "Toutes les LEDs"),
    ]

    led = models.CharField(max_length=10, choices=LED_CHOICES)
    nom_plage = models.CharField(max_length=100)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    actions = models.CharField(max_length=20)  # Assurez-vous que ce champ est ajouté

    def __str__(self):
        return f"{self.nom_plage} - {self.led} ({self.heure_debut} - {self.heure_fin})"

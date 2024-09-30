from django.db import models

class PlageHoraire(models.Model):
    LED_CHOICES = [
        ('LED1', "LED1"),
        ('LED2', "LED2"),
    ]

    ACTION_CHOICES = [
        ('allumer', "Allumer"),
        ('eteindre', "Éteindre"),
    ]

    led = models.CharField(max_length=4, choices=LED_CHOICES)
    nom_plage = models.CharField(max_length=20)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    actions = models.CharField(max_length=8, choices=ACTION_CHOICES)

    def __str__(self):
        return f"{self.nom_plage} ({self.heure_debut} - {self.heure_fin})"

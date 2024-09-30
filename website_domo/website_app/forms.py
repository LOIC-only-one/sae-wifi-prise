from django import forms

class Prise1FormHoraire(forms.Form):
    
    CHOICES  = [
        ('LED1', "LED1"),
        ('LED2', "LED2"),
    ]
    
    led = forms.ChoiceField(choices=CHOICES)
    
    nom_plage = forms.CharField(
        label="Nom de la plage", 
        max_length=20
    )
    heure_debut = forms.TimeField(
        label="Heure de début",
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
    )
    
    heure_fin = forms.TimeField(
        label="Heure de fin",
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
    )
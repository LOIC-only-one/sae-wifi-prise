from django import forms
from .models import PlageHoraire

class Prise1ModelForm(forms.ModelForm):
    class Meta:
        model = PlageHoraire
        fields = ['led', 'nom_plage', 'heure_debut', 'heure_fin']
        widgets = {
            'heure_debut': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }
        labels = {
            'led': '💡 LED',
            'nom_plage': 'Nom de la plage',
            'heure_debut': 'Heure de début',
            'heure_fin': 'Heure de fin',
        }

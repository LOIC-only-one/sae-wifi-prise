from django import forms
from .models import PlageHoraire, Settings

class Prise1ModelForm(forms.ModelForm):
    ACTION_CHOICES = [
        ('allumer', "Allumer"),
        ('eteindre', "Éteindre"),
    ]
    
    actions = forms.ChoiceField(choices=ACTION_CHOICES, label='Action')

    class Meta:
        model = PlageHoraire
        fields = ['led', 'nom_plage', 'heure_debut', 'heure_fin', 'actions']  # Ajout du champ actions ici
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



class SettingsModelForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['numero_telephone', 'serveur_smtp', 'port_smtp', 'email_expediteur', 'mot_de_passe', 'email_destinataire']
        widgets = {
            'mot_de_passe': forms.PasswordInput(),
        }
        labels = {
            'numero_telephone': 'Numéro de téléphone',
            'serveur_smtp': 'Serveur SMTP',
            'port_smtp': 'Port SMTP',
            'email_expediteur': 'Email expéditeur',
            'mot_de_passe': 'Mot de passe',
            'email_destinataire': 'Email destinataire',
        }
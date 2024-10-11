
from .models import Settings

def get_settings():
    try:
        settings = Settings.objects.get(id=0)
        return {
            'numero_telephone': settings.numero_telephone,
            'serveur_smtp': settings.serveur_smtp,
            'port_smtp': settings.port_smtp,
            'email_expediteur': settings.email_expediteur,
            'mot_de_passe': settings.mot_de_passe,
            'email_destinataire': settings.email_destinataire,
        }
    except Settings.DoesNotExist:
        raise Exception("Les paramètres de configuration n'existent pas.")
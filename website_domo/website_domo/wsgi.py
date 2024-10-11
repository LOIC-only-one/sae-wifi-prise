import os
import sys

# Ajoutez le chemin à sys.path
sys.path.append('/home/pi/Desktop/sae-wifi-prise/website_domo')

# Définissez le paramètre d'environnement
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website_domo.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

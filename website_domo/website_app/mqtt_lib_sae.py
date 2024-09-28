# /usr/bin/python

## Author Maurer Loïc
## Université Haute Alsace

import paho.mqtt.client as mqtt
import logging
import time
import threading
from colorama import Fore, Style, init

init(autoreset=True)

class MqttConnexion:

    USERNAME = "serveur-rpi"

    def __init__(self, broker: str = "broker.Id00l.eu", port: int = 14022, topic: str = "alpha/1") -> None:
        self.broker = broker
        self.port = port
        self.topic = topic

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def give_feedback(self, message, feedback_topic):
        """Envoi d'un message de feedback sur un TOPIC
        
        :param message : Message à envoyer sur le topic
        :type message : str
        
        :param feedback_topic : Topic sur lequel envoyer le feedback
        :type feedback_topic : str
        
        """
        feed = f"Envoi de feedback : {message} sur le topic {feedback_topic}"
        logging.info(feed)
        publication = self.client.publish(feedback_topic, message)
        
        if publication.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"{Fore.GREEN}Message '{message}' publié avec succès sur {feedback_topic}{Style.RESET_ALL}")
        else:
            logging.error(f"Échec de la publication sur {feedback_topic}")

    def state_led(self, message, led_topic="sae301/led"):
        """Envoi du message d'état à la LED
        
        :param message : Message à envoyer sur le topic
        :type message : str
        
        :param led_topic : Topic sur lequel envoyer le message
        :type led_topic : str : default to sae301/led
        """
        result = self.client.publish(led_topic, message)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"{Fore.GREEN}Message '{message}' publié avec succès sur {led_topic}{Style.RESET_ALL}")
        else:
            logging.error(f"Échec de la publication sur {led_topic}")

    def get_temp(self, temp_topic='sae301/temperature'):
        """Souscription au topic de température
        
        :param temp_topic : Topic à s'abonner pour la température
        :type temp_topic : str default to sae301/temperature
        
        """
        self.client.subscribe(temp_topic)
        logging.info(f"{Fore.YELLOW}Souscription au topic : {temp_topic}{Style.RESET_ALL}")


    def handle_light(self,action):
        if action == "lumiere1_on":
            self.state_led("LED_ON")
            self.give_feedback("LED_ON")
        elif action == "lumiere1_off":
            self.state_led("LED_OFF")
            self.give_feedback("LED_OFF")
        elif action == "lumiere2_on":
            self.state_led("LED_ON")
            self.give_feedback("LED_ON")
        elif action == "lumiere2_off":
            self.state_led("LED_OFF")
            self.give_feedback("LED_OFF")
        elif action == "all_on":
            self.state_led("LED_ON") and self.state_led("LED_ON")
            self.give_feedback("LEDS ALLUMEES")
        elif action == "all_off":
            self.state_led("LED_OFF") and self.state_led("LED_OFF")
            self.give_feedback("LEDS ETEINTES")
        
##################################################################
##################################################################
####################Fonction de la doc Paho#######################


    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback appelé lors de la connexion au broker"""
        if reason_code == 0:
            logging.info("Connexion au broker réussie :)")
            client.subscribe(self.topic)
            logging.info(f"{Fore.YELLOW}Abonné au topic : {self.topic}{Style.RESET_ALL}")
        else:
            logging.error(f"Erreur de connexion : {reason_code}")

    def on_message(self, client, userdata, msg):
        """Callback appelé lorsqu'un message est reçu"""
        message = str(msg.payload.decode())
        logging.info(f"{self.USERNAME} : {msg.topic} : {message}")

    def on_disconnect(self, client, userdata, rc):
        """Callback appelé lors de la déconnexion"""
        logging.info(f"Déconnexion avec le code de retour {rc}")


    def handle_connexion(self):
        """Gère la connexion au broker MQTT et écoute les messages"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_forever()
        except Exception as e:
            logging.error(f"Erreur lors de la connexion ou pendant la réception des messages : {str(e)}")
        finally:
            self.client.disconnect()
            logging.info("Déconnecté du broker")



########################################################################
########################################################################
########################################################################
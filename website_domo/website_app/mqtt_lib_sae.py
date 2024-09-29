#!/usr/bin/python

## Author: Maurer Loïc
## Université Haute Alsace

import paho.mqtt.client as mqtt
import logging
from colorama import Fore, Style, init

init(autoreset=True)

class MqttConnexion:

    USERNAME = "serveur-rpi"

    def __init__(self, broker: str = "broker.id00l.eu", port: int = 14022) -> None:
        self.broker = broker
        self.port = port

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.last_temp = None

    def give_feedback(self, message, feedback_topic):
        """Envoi d'un message de feedback sur un TOPIC
        
        :param message : Message envoyé au topic
        :type message : str
        
        :param feedback_topic : Topic sur lequel est envoyé le message
        :type feedback_topic : str
        """
        feed = f"Envoi de feedback : {message} sur le topic {feedback_topic}"
        logging.info(feed)
        publication = self.client.publish(feedback_topic, message)
        
        if publication.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"{Fore.GREEN}Message '{message}' publié avec succès sur {feedback_topic}{Style.RESET_ALL}")
        else:
            logging.error(f"Échec de la publication sur {feedback_topic}")

    def state_led(self, message, led_topic):
        """Envoi du message d'état à la LED
        
        :param message : Message envoyé sur le topic
        :type message : str
        
        :param led_topic : Topic sur lequel est instructions sont envoyé
        :type led_topic : str
        
        """
        result = self.client.publish(led_topic, message)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"{Fore.GREEN}Message '{message}' publié avec succès sur {led_topic}{Style.RESET_ALL}")
        else:
            logging.error(f"Échec de la publication sur {led_topic}")

    def get_temp(self):
        """Récupère la dernière température reçue
        
        :return self.last_temp : Température du client mqtt créer
        :rtype : str
        """
        return self.last_temp if self.last_temp else "Température indisponible"   

    def handle_light(self, action):
        """Gestion des différentes actions du site web
        
        :param action : Action générée pour la LED
        :type action : str
        """
        led_topic_1 = "sae301/led"
        led_topic_2 = "sae301_2/led"

        if action == "lumiere1_on":
            self.state_led("LED_ON", led_topic_1)
            self.give_feedback("LED_ON", "sae301/led/status")
        elif action == "lumiere1_off":
            self.state_led("LED_OFF", led_topic_1)
            self.give_feedback("LED_OFF", "sae301/led/status")
        elif action == "lumiere2_on":
            self.state_led("LED_ON", led_topic_2)
            self.give_feedback("LED_ON", "sae301_2/led/status")
        elif action == "lumiere2_off":
            self.state_led("LED_OFF", led_topic_2)
            self.give_feedback("LED_OFF", "sae301_2/led/status")
        elif action == "all_on":
            self.state_led("LED_ON", led_topic_1)
            self.state_led("LED_ON", led_topic_2)
            self.give_feedback("LEDS ALLUMEES", "sae301/led/status")
        elif action == "all_off":
            self.state_led("LED_OFF", led_topic_1)
            self.state_led("LED_OFF", led_topic_2)
            self.give_feedback("LEDS ETEINTES", "sae301/led/status")
            
########################################################################
########################################################################
########################################################################            


    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback appelé lors de la connexion au broker BY phaho
        
        :param client : Client MQTT créer dans __init__
        :param resean_code : Code de retour d'une requete du client
        
        :type reason_code : str
        
        """
        if reason_code == 0:
            logging.info("Connexion au broker réussie :)")
            client.subscribe("sae301/temperature")
            logging.info(f"{Fore.YELLOW}Abonné au topic : sae301/temperature{Style.RESET_ALL}")
        else:
            logging.error(f"Erreur de connexion : {reason_code}")

    def on_message(self, client, userdata, msg):
        """Callback appelé lorsqu'un message est reçu BY phaho
        
        :param msg : Message reçu par le client
        :type msg : str
        
        """
        message = str(msg.payload.decode())
        logging.info(f"{self.USERNAME} : {msg.topic} : {message}")

        if msg.topic == 'sae301/temperature':
            self.last_temp = message

    def on_disconnect(self, client, userdata, rc):
        """Callback appelé lors de la déconnexion BY phaho
        
        REFONT_en_COUR
        
        """
        logging.info(f"Déconnexion avec le code de retour {rc}")

    def handle_connexion(self):
        """Gère la connexion au broker MQTT et écoute les messages"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Erreur lors de la connexion ou pendant la réception des messages : {str(e)}")
########################################################################
########################################################################
########################################################################
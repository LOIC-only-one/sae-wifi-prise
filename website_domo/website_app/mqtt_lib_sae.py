#!/usr/bin/python

import paho.mqtt.client as mqtt
import logging
from colorama import Fore, Style, init
from datetime import datetime, time
import threading

init(autoreset=True)

class MqttConnexion:
    USERNAME = "serveur-rpi"
    USERNAME_MQTT = "pi" 
    PASSWORD_MQTT = "pi" 

    def __init__(self, broker: str = "broker.id00l.eu", port: int = 14022) -> None:
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.last_temp = None
        self.client.username_pw_set(self.USERNAME_MQTT, self.PASSWORD_MQTT)

    def give_feedback(self, message, feedback_topic):
        feed = f"Envoi de feedback : {message} sur le topic {feedback_topic}"
        logging.info(feed)
        publication = self.client.publish(feedback_topic, message)
        
        if publication.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"{Fore.GREEN}Message '{message}' publié avec succès sur {feedback_topic}{Style.RESET_ALL}")
        else:
            logging.error(f"Échec de la publication sur {feedback_topic}")

    def state_led(self, message, led_topic):
        result = self.client.publish(led_topic, message)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"{Fore.GREEN}Message '{message}' publié avec succès sur {led_topic}{Style.RESET_ALL}")
        else:
            logging.error(f"Échec de la publication sur {led_topic}")

    def get_temp(self):
        return self.last_temp if self.last_temp else "Température indisponible"

    def schedule_plage_horaire(self, plage):
        now = datetime.now().time()

        if plage.heure_debut <= now <= plage.heure_fin:
            if plage.actions == 'allumer':
                self.handle_light(f"lumiere{plage.led[-1]}_on")
            else:
                self.handle_light(f"lumiere{plage.led[-1]}_off")
        
        if now >= plage.heure_fin:
            if plage.actions == 'allumer':
                self.handle_light(f"lumiere{plage.led[-1]}_off")
            else:
                self.handle_light(f"lumiere{plage.led[-1]}_on")

    def monitor_plages(self, plages):
        def run():
            while True:
                now = datetime.now().time()
                for plage in plages:
                    self.schedule_plage_horaire(plage)
                time.sleep(60)

        threading.Thread(target=run, daemon=True).start()

    def handle_light(self, action):
        led_topic_1 = "sae301/led"
        led_topic_2 = "sae301_2/led"

        if action == "lumiere1_on":
            self.publication(led_topic_1, "LED_ON")
        elif action == "lumiere1_off":
            self.publication(led_topic_1, "LED_OFF")
        elif action == "lumiere2_on":
            self.publication(led_topic_2, "LED_ON")
        elif action == "lumiere2_off":
            self.publication(led_topic_2, "LED_OFF")
        elif action == "all_on":
            self.publication(led_topic_1, "LED_ON")
            self.publication(led_topic_2, "LED_ON")
        elif action == "all_off":
            self.publication(led_topic_1, "LED_OFF")
            self.publication(led_topic_2, "LED_OFF")

    def publication(self, topic, message):
        self.client.publish(topic, message)
    
    def souscription(self, topic):
        self.client.subscribe(topic=topic)

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            logging.info("Connexion au broker réussie :)")
            client.subscribe("sae301/temperature")
            logging.info(f"{Fore.YELLOW}Abonné au topic : sae301/temperature{Style.RESET_ALL}")
        else:
            logging.error(f"Erreur de connexion : {reason_code}")

    def on_message(self, client, userdata, msg):
        message = str(msg.payload.decode())
        logging.info(f"{self.USERNAME} : {msg.topic} : {message}")

        if msg.topic == 'sae301/temperature':
            self.last_temp = message

    def on_disconnect(self, client, userdata, rc):
        logging.info(f"Déconnexion avec le code de retour {rc}")

    def handle_connexion(self):
        try:
            self.client.username_pw_set("pi", "pi") 
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Erreur lors de la connexion ou pendant la réception des messages : {str(e)}")


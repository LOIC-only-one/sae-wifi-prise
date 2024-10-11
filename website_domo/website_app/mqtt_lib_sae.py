#!/usr/bin/python

import paho.mqtt.client as mqtt
import logging
from colorama import Fore, Style, init
from datetime import datetime, time
import threading
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .config import get_settings
import os


init(autoreset=True)

class MqttConnexion:
    USERNAME = "serveur-rpi"
    USERNAME_MQTT = "pi" 
    PASSWORD_MQTT = "pi" 

    def __init__(self, broker: str = "broker.id00l.eu", port: int = 14022) -> None:
        self.settings = get_settings()
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.last_temp = None
        self.client.username_pw_set(self.USERNAME_MQTT, self.PASSWORD_MQTT)
        self.alert = False
        
        self.account_sid = 'ACc8de5270e0cc9e4029bbd7f6c718b59b'
        self.auth_token = 'cd379424575f1e98829742c0966f655b'
        self.sms_client = Client(self.account_sid, self.auth_token)

        self.email_expediteur = self.settings["email_expediteur"]
        self.mot_de_passe = self.settings["mot_de_passe"]
        self.email_destinataire = self.settings["email_destinataire"]
        self.serveur_smtp = self.settings["serveur_smtp"]
        self.port_smtp = self.settings["port_smtp"]
        self.numero_telephone = self.settings["numero_telephone"]

        self.state_led_info= {
            "led1" : "off",
            "led2" : "off",
        }

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

    def handle_light(self, action):
        if action == "lumiere1_on":
            self.publication("sae301/led", "LED_ON")
            self.state_led_info["led1"] = "on"
            self.client.publish("sae301/status", "ON")
        elif action == "lumiere1_off":
            self.publication("sae301/led", "LED_OFF")
            self.state_led_info["led1"] = "off"
            self.client.publish("sae301/status", "OFF")
        elif action == "lumiere2_on":
            self.publication("sae301_2/led", "LED_ON")
            self.state_led_info["led2"] = "on"
            self.client.publish("sae301_2/status", "ON")
        elif action == "lumiere2_off":
            self.publication("sae301_2/led", "LED_OFF")
            self.state_led_info["led2"] = "off"
            self.client.publish("sae301_2/status", "OFF")
        elif action == "all_on":
            self.publication("sae301/led", "LED_ON")
            self.publication("sae301_2/led", "LED_ON")
            self.state_led_info["led1"] = "on"
            self.state_led_info["led2"] = "on"
            self.client.publish("sae301/status", "ON")
            self.client.publish("sae301_2/status", "ON")
        elif action == "all_off":
            self.publication("sae301/led", "LED_OFF")
            self.publication("sae301_2/led", "LED_OFF")
            self.state_led_info["led1"] = "off"
            self.state_led_info["led2"] = "off"
            self.client.publish("sae301/status", "OFF")
            self.client.publish("sae301_2/status", "OFF")
            
    def publication(self, topic, message):
        self.client.publish(topic, message)
    
    def souscription(self, topic):
        self.client.subscribe(topic=topic)
        
    def send_email(self,message="La température de la pièce est anormalement élevée", subject="Alerte température"):
        msg = MIMEMultipart()
        msg['From'] = self.email_expediteur
        msg['To'] = self.email_destinataire
        msg['Subject'] = "Alerte température"
        message = "La température de la pièce est anormalement élevée"
        msg.attach(MIMEText(message, 'plain'))

        try:
            with smtplib.SMTP(self.serveur_smtp, self.port_smtp) as server:
                server.starttls()
                server.login(self.email_expediteur, self.mot_de_passe)
                server.send_message(msg)
                logging.info(f"Email envoyé à {self.email_destinataire} avec succès.")
        except Exception as e:
            logging.error(f"Échec de l'envoi de l'email : {str(e)}")
            
    def send_sms(self, message="Alerte température"):
        try:
            self.sms_client.messages.create(
                body=message,
                from_='+12028997451',
                to=self.numero_telephone
            )
            logging.info("SMS envoyé avec succès.")
        except Exception as e:
            logging.error(f"Échec de l'envoi du SMS : {str(e)}")
            
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            logging.info("Connexion au broker réussie :)")
            topics = [
                "sae301/temperature",
                "sae301/temperature/status",
                "sae301/led/status",
                "sae301_2/led/status"
            ]
            for topic in topics:
                client.subscribe(topic)
                logging.info(f"{Fore.YELLOW}Abonné au topic : {topic}{Style.RESET_ALL}") 
        else:
            logging.error(f"Erreur de connexion : {reason_code}")

    def on_message(self, client, userdata, msg):
        message = str(msg.payload.decode())
        logging.info(f"{self.USERNAME} : {msg.topic} : {message}")

        if msg.topic == 'sae301/temperature':
            self.last_temp = message
        
        elif msg.topic == 'sae301/led/status':
            self.state_led_info["led1"] = "on" if message == "ON" else "off"

        elif msg.topic == 'sae301_2/led/status':
            self.state_led_info["led2"] = "on" if message == "ON" else "off"

        elif msg.topic == 'sae301/temperature/status':
            message = msg.payload.decode('utf-8')
            self.alert = "Température élevée"
            
            if self.alert in message:
                self.send_email()
                self.send_sms()

        logging.info(f"État des LEDs : LED1 {self.state_led_info['led1']} et LED2 {self.state_led_info['led2']}")


    def handle_connexion(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Erreur lors de la connexion ou pendant la réception des messages : {str(e)}")

    def on_disconnect(self, client, userdata, rc):
        logging.info(f"Déconnecté avec le code de résultat: {rc}")
        
    
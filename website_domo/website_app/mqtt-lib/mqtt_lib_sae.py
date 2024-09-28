import paho.mqtt.client as mqtt
import logging
import time


class MqttConnexion:

    USERNAME = "serveur-rpi"

    def __init__(self, broker: str = "broker.Id00l.eu", port: int = 14022, topic: str = "alpha/1") -> None:
        """
        :param broker: Broker MQTT (adresse IP ou URL)
        :param port: Port du broker MQTT
        :param topic: Topic MQTT auquel s'abonner
        Constructeur de ma classe de connexion pour la SAE python
        """
        self.broker = broker
        self.port = port
        self.topic = topic

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    #### Fonction logique SAE

    def give_feedback(self, message, feedback_topic):
        """
        Méthode d'envoi d'un message de FEEDBACK sur un TOPIC
        
        :message : Message de feedback : default to state_led
        :type message : str
        """
        feed = f"Envoi de feedback : {message} sur le topic {feedback_topic}"
    
        logging.info(feed)
        publication = self.client.publish(feedback_topic, message)
        
        if publication.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"Message '{message}' publié avec succès sur {feedback_topic}")
        else:
            logging.error(f"Échec de la publication sur {feedback_topic}")
            
            
    def state_led(self, message):
        """
        Méthode d'envoi du message d'état à la LED, si message "ON", alors envoi sur le topic associé le message, sinon "OFF" pour éteindre.
        
        :message : Message d'état envoyé au topic
        :type message : str
        
        :return : Une chaîne de caractères de logging
        :rtype : str
        """
        
        TOPIC = "sae301/led/status"
        result = self.client.publish(TOPIC, message)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"Message '{message}' publié avec succès sur {TOPIC}")
        else:
            logging.error(f"Échec de la publication sur {TOPIC}")

    #### Fonction documentation PAHO-MQTT

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        """
        Callback appelé lorsque le script se connecte au broker
        :param client : Instance du client
        :reason_code : Code de retour du client
        :properties  : Paramètre : default to None
        """
        if reason_code == 0:
            logging.info("Connexion au broker réussie :)")
            client.subscribe(self.topic)
            logging.info(f"Abonné au topic : {self.topic}")
        else:
            logging.error(f"Erreur de connexion : {reason_code}")

    #### Réaction pour la capture d'un message

    def on_message(self, client, userdata, msg):
        """
        Callback appelé lorsqu'un message est reçu
        """
        message = str(msg.payload.decode())
        logging.info(f"{self.USERNAME} : {msg.topic} : {message}")
        
        if message == "ON":
            logging.info("LED allumée")
            self.state_led("ON")
        elif message == "OFF":
            logging.info("LED éteinte")
            self.state_led("OFF")
        else:
            logging.warning(f"Message non reconnu : {message}")

    def on_disconnect(self, client, userdata, rc):
        FIRST_RECONNECT_DELAY = 1
        RECONNECT_RATE = 2
        MAX_RECONNECT_COUNT = 12
        MAX_RECONNECT_DELAY = 60

        logging.info(f"Déconnexion avec le code de retour {rc}")
        
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        
        while reconnect_count < MAX_RECONNECT_COUNT:
            logging.info(f"Tentative de reconnexion dans {reconnect_delay} secondes...")
            time.sleep(reconnect_delay)
            
            try:
                client.reconnect()
                logging.info("Reconnecté avec succès !")
                return
            except Exception as err:
                logging.error(f"Échec de la tentative de reconnexion : {err}")
            
            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        
        logging.error("Échec de la reconnexion après plusieurs tentatives. Abandon.")

    def handle_connexion(self):
        """
        Méthode pour gérer la connexion au broker MQTT et écouter les messages
        """
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_forever()
        except Exception as e:
            logging.error(f"Erreur lors de la connexion ou pendant la réception des messages : {str(e)}")
        finally:
            self.client.disconnect()
            logging.info("Déconnecté du broker")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    mqtt_connexion = MqttConnexion(topic="sae301/led/status")
    
    try:
        mqtt_connexion.client.connect(mqtt_connexion.broker, mqtt_connexion.port, 60)
        
        # Publication de l'état de la LED
        mqtt_connexion.state_led("ON")
        
        # Envoi d'un message de feedback sur un autre topic
        mqtt_connexion.give_feedback("LED allumée", "sae301/led/log")
        
        # Boucle pour écouter les messages MQTT
        mqtt_connexion.client.loop_forever()
    except Exception as e:
        logging.error(f"Erreur lors de la connexion ou pendant la réception des messages : {str(e)}")
    finally:
        mqtt_connexion.client.disconnect()
        logging.info("Déconnecté du broker")

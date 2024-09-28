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


    #### Fonction logique SAE

    def give_feedback(self, message):
        """
        Methode d'envoi d'un message de FEEDBACK sur un TOPIC
        
        :message : Message de feedback : default to state_led
        :type message : str
         
        """

        ## S'occupe de gerer les retours dans un autre topic

    def state_led(self,message):
        """
        Methode d'envoi du message d'état à la LED, si message "ON", alors envois sur le topic associé le message, sinon "OFF" pour eteindre.
        
        :message : Message d'état envoyé au topic
        :type message : str
        
        :return : Une chaine de caractère de logging
        :rtype : str
        
        """

        pass

        ## Traiter la logique d'eteinte et d'allumage de la led esp


    #### Fonction documentation PAHO-MQTT

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        """
        Callback appelé lorsque le script se connect au broker
        :param client : Instance du client
        :reason_code : Code de retour de client
        :properties  : Paramètre : default to None
        """
        if reason_code == 0:
            print("Connexion au broker OK :)")
            client.subscribe(self.topic)
            print(f"Abonné au topic : {self.topic}")
        else:
            print(f"Erreur de connexion : {reason_code}")


    #### Réaction pour la capture d'un message

    def on_message(self, client, userdata, msg):
        """
        Callback appelé lorsqu'un message est reçu
        """
        message = str(msg.payload.decode())
        print(f"{self.USERNAME} : {msg.topic} : {message}")
        
        if message == "comment ca va":
            print("Message detecter !")


    def on_disconnect(self, client, date, rc):
        FIRST_RECONNECT_DELAY = 1
        RECONNECT_RATE = 2
        MAX_RECONNECT_COUNT = 12
        MAX_RECONNECT_DELAY = 60

        logging.info("Déconnexion avec le code de retour ", rc)
        
        reconnect_count , reconnect_delay = 0, FIRST_RECONNECT_DELAY
        
        while reconnect_count < MAX_RECONNECT_COUNT:
            logging.info("Entrain de se reconnecter in ... ", reconnect_delay, " seconds!")
            time.sleep(reconnect_delay)        

        try:
            client.reconnect()
            logging.info("Reconnecté avec succes !")
            return
        except Exception as err:
            logging.error("Echec de la la tentative de reconnect !")
        
        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

    
    
    def handle_connexion(self):
        """
        Méthode pour gérer la connexion au broker MQTT et écouter les messages
        """
        mqttc = mqtt.Client()
        mqttc.on_connect = self.on_connect
        mqttc.on_message = self.on_message

        try:
            mqttc.connect(self.broker, self.port, 60)
            mqttc.loop_forever()
        except Exception as e:
            print(f"Erreur lors de la connexion ou pendant la réception des messages : {str(e)}")
        finally:
            mqttc.disconnect()
            print("Déconnecté du broker")

if __name__ == "__main__":
    mqtt_connexion = MqttConnexion(topic="alpha/1")
    mqtt_connexion.handle_connexion()

import paho.mqtt.client as mqtt

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

    def give_feedback(self,topic):

        pass

        ## S'occupe de gerer les retours dans un autre topic

    def state_led(self,message):

        pass

        ## Traiter la logique d'eteinte et d'allumage de la led esp


    #### Fonction documentation PAHO-MQTT

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        """
        Callback appelé lorsque le client se connecte au broker
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

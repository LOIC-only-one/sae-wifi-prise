import paho.mqtt.client as mqtt

# Callback appelé quand la connexion au broker est établie
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker avec succès")
        # S'abonner au topic souhaité
        client.subscribe("alpha/1")
    else:
        print(f"Échec de la connexion, code de retour : {rc}")

# Callback appelé lorsqu'un message est reçu
def on_message(client, userdata, msg):
    print(f"Message reçu sur le topic {msg.topic}: {msg.payload.decode()}")

# Configuration du client MQTT
client = mqtt.Client()

# Assignation des callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker MQTT (remplacez par l'IP/URL du broker)
broker_address = "broker.id00l.eu"
client.connect(broker_address, 14022, 60)

client.loop_forever()

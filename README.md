# SAE-WiFi-Prise

## Description
Ce projet consiste à développer une prise connectée intelligente WiFi dans le cadre du cours **SAE301** à l'IUT de Colmar. 

La solution intègre :
- Une **carte électronique** basée sur un ESP8266.
- Un serveur web hébergé sur un Raspberry Pi.
- Une application Android pour le contrôle à distance.
- Un capteur de température **DS18B20**.
- La gestion des plages horaires pour l'allumage et l'extinction des LEDs via MQTT.

## Fonctionnalités
- **Contrôle via MQTT** : Gestion des LEDs connectées via des topics MQTT.
- **Notification en temps réel** : Réception de notifications sur l'état des LEDs et la température.
- **Interface utilisateur** : Une application web et mobile pour interagir avec la prise connectée.
- **Sécurité** : Configuration sécurisée avec des règles NAT et un DNS personnalisé.
- **Gestion des plages horaires** : Automatisation de l'allumage/extinction des LEDs.

## Technologies utilisées
- **Matériel** :
  - Raspberry Pi
  - ESP8266
  - Capteur DS18B20
- **Logiciels** :
  - Django pour le backend web
  - Paho MQTT pour la communication MQTT
  - Apache2 comme serveur web
  - Android Studio pour l'application mobile
- **Protocoles** : MQTT, HTTP/HTTPS

## Utilisation
1. Accéder à l'interface web via l'URL du serveur.
2. Ajouter des plages horaires pour automatiser les LEDs.
3. Contrôler manuellement les LEDs via l'application Android ou le site web.

## Structure du projet
```
sae-wifi-prise/
├── website_domo/      # Application Django
└── README.md          # Ce fichier
```

# Projet de Système de Télésurveillance avec Arduino Yun Rev 2 et un stockage en Cloud AWS via une interface python

## Description

Ce projet de système de télésurveillance utilise la carte Arduino Yun Rev 2 en conjonction avec un capteur de mouvement PIR (Passive Infrared) et une webcam USB. L'Arduino Yun Rev 2 est basé sur le système Linux OpenWRT intégré, permettant ainsi d'utiliser les bibliothèques bridges pour interagir avec le système d'exploitation Linux.

Le fonctionnement du système est le suivant : lorsqu'un mouvement est détecté par le capteur PIR, l'Arduino Yun Rev 2 déclenche une capture d'image avec la webcam USB connectée. Cette image est ensuite visualisée sur une interface Python qui comprend une page de flux d'images, une page de flux vidéo, une page d'accueil et une page de connexion.

De plus, le code Arduino responsable de la gestion de ce processus est situé dans le fichier nommé "code_arduino.ino" inclus dans ce dépôt.

En outre, le système offre la possibilité de réaliser un streaming vidéo qui peut être récupéré via HTTP dans un réseau Wi-Fi en utilisant une adresse IP spécifique.

## Fonctionnalités

- Détection de mouvement avec le capteur PIR
- Capture d'image avec une webcam USB
- Interface Python avec pages de flux d'images, flux vidéo, accueil et connexion
- Possibilité de réaliser un streaming vidéo dans un réseau Wi-Fi

## Configuration et Utilisation

1. Assurez-vous que l'Arduino Yun Rev 2 est correctement connecté au capteur PIR et à la webcam USB.
2. Chargez le code Arduino "code_arduino.ino" dans l'Arduino Yun Rev 2.
3. Démarrez le système et observez les réactions en cas de détection de mouvement.
4. Accédez à l'interface Python pour visualiser les images capturées et le flux vidéo.

## Structure du Projet

- **code_arduino.ino**: Code Arduino pour la gestion de la détection de mouvement et des captures d'image.
- **interface_python/**: Répertoire contenant le code source de l'interface Python.
  - **flux_image.py**: Page de flux d'images.
  - **flux_video.py**: Page de flux vidéo.
  - **accueil.py**: Page d'accueil.
  - **login.py**: Page de connexion.

## Configuration Réseau

1. Connectez-vous au réseau Wi-Fi approprié.
2. Obtenez l'adresse IP de l'Arduino Yun Rev 2.
3. Utilisez l'adresse IP pour accéder aux pages de l'interface Python et récupérer le streaming vidéo.

## Remarque Importante

Assurez-vous d'avoir correctement configuré votre Arduino Yun Rev 2 et installé toutes les bibliothèques nécessaires pour garantir le bon fonctionnement du projet.

---

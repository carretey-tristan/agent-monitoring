🖥️ Agent de Monitoring Système – Windows
📌 Description
Cet agent de monitoring a pour objectif de surveiller les performances d’un ordinateur sous Windows. Il collecte en temps réel diverses métriques système (CPU, RAM, disque, réseau, mises à jour Windows) et les envoie vers une base de données InfluxDB. Une interface en systray (barre des tâches) permet de contrôler facilement l'agent : démarrage, pause, consultation des logs et arrêt.

🚀 Fonctionnalités
Collecte automatique de métriques :

Utilisation CPU, RAM, disque

Trafic réseau

Mises à jour Windows

Informations système

Transmission vers InfluxDB :

Envoi sécurisé des données avec tags personnalisés (nom de l’hôte, entreprise)

Interface utilisateur via icône en barre de tâche :

Démarrage / Pause de la collecte

Ouverture des logs

Arrêt de l’agent

Configuration sécurisée :

Données sensibles chiffrées avec Fernet (URL, token, etc.)

📦 Prérequis
Environnement logiciel
Windows

Python 3.12 ou supérieur

InfluxDB (accessible via une URL/API)

Installation des dépendances
Installez les bibliothèques nécessaires :


pip install -r requirements.txt
🗂️ Structure du projet

agent_test/
├── chiffre.py           # Chiffrement/déchiffrement de config.ini
├── config.ini           # Fichier de configuration (chiffré ou non)
├── cpu_info.py          # Collecte CPU
├── disk_info.py         # Collecte disque
├── icon.ico             # Icône principale de l'application
├── images/              # Icônes pour différents états
│   ├── logo_monitoring.png
│   ├── logo_monitoring_pause.png
│   └── logo_monitoring_broke.png
├── main.py              # Script principal de l’agent
├── network_info.py      # Collecte réseau
├── ram_info.py          # Collecte RAM
├── requirements.txt     # Dépendances Python
├── system_info.py       # Infos système générales
├── windows_update.py    # Mises à jour Windows
├── README.md            # Ce fichier
└── __pycache__/         # Cache Python
⚙️ Utilisation
1. Configuration initiale
Editez ou déchiffrez le fichier config.ini :


python chiffre.py decrypt config.ini
Contenu type :


[general]
name = NomDuPC
company = NomDeLEntreprise

[influxdb]
url = https://influxdb.example.com
token = VotreToken
org = VotreOrganisation
bucket = VotreBucket
Chiffrez ensuite le fichier :


python chiffre.py encrypt config.ini
2. Lancement de l’agent
Exécutez le script principal :


python main.py
Une icône apparaîtra dans la barre des tâches. Un clic droit dessus permet de :

Démarrer / mettre en pause la collecte

Ouvrir les logs

Quitter l’application

🔧 Ajouter une nouvelle métrique
Créez un fichier, ex. new_metric.py

Implémentez une fonction :


def get_data():
    return {"nom_de_la_métrique": valeur}
Intégrez-la dans main.py :


import new_metric
...
"new_metric": new_metric.get_data(),


👤 Auteur
Nom : Tristan Carretey

Formation : BTS SIO

Établissement : Lycée Suzanne Valadon

Contact : carretey.tristan@proton.me

📝 Remarques
En cas de problème, consultez le fichier agent.log.

Vérifiez que toutes les dépendances sont installées avant de démarrer l'agent.
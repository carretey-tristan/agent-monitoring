"""
Agent de monitoring système - Script principal
----------------------------------------------
Ce script constitue le cœur d'un agent Windows qui surveille les performances système (CPU, RAM, disque, mises à jour, trafic réseau, etc.)
- Il lit une configuration chiffrée, l'interprète et s'assure qu'un nom de machine et une entreprise soient définis.
- Il collecte des métriques à intervalles réguliers et les envoie dans InfluxDB.
- Il fournit une icône en barre de tâche (systray) pour démarrer/mettre en pause/lancer les logs/fermer.

Technologies utilisées :
- psutil, cryptography, pystray, tkinter, InfluxDB Client
"""

import time
import threading
import configparser
import os
import base64
import hashlib
import tkinter as tk
import psutil
from tkinter import simpledialog

from datetime import datetime, timezone
from cryptography.fernet import Fernet
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from pystray import Icon, MenuItem, Menu
from PIL import Image

import system_info
import cpu_info
import ram_info
import disk_info
import windows_update
import network_info


# === CONFIGURATION CHIFFREMENT === #
def generate_key(password: str) -> bytes:
    """
    Génére une clé Fernet à partir d'un mot de passe (hash SHA-256 + base64).
    """
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def decrypt_ini(file_path: str, key: bytes):
    """
    Déchiffre un fichier INI contenant des valeurs chiffrées avec Fernet.
    Ignore la section [general] qui est supposée être en clair.
    """
    config = configparser.ConfigParser()
    config.read(file_path)
    fernet = Fernet(key)

    for section in config.sections():
        if section == "general":
            continue  # Ne pas décrypter cette section
        for option in config[section]:
            try:
                decrypted = fernet.decrypt(config[section][option].encode()).decode()
                config[section][option] = decrypted
            except Exception as e:
                print(f"Erreur déchiffrement [{section}]->{option}: {e}")

    return config

# === INITIALISATION DU NOM ET DE L'ENTREPRISE === #
def ensure_general_section(config_path):
    """
    Vérifie que le fichier INI contient un nom de machine et un nom d'entreprise.
    Si absent, les demande via des boîtes de dialogue tkinter et les écrit dans le fichier.
    """
    config_parser = configparser.ConfigParser()
    config_parser.read(config_path)

    if "general" not in config_parser:
        config_parser.add_section("general")

    name = config_parser["general"].get("name", "").strip()
    company = config_parser["general"].get("company", "").strip()

    if not name or not company:
        root = tk.Tk()
        root.withdraw()  # Cache la fenêtre principale

        if not name:
            name = simpledialog.askstring("Nom de la machine", "Entrez le nom personnalisé de ce PC :")
            if name:
                config_parser["general"]["name"] = name

        if not company:
            company = simpledialog.askstring("Entreprise", "Entrez le nom de l'entreprise :")
            if company:
                config_parser["general"]["company"] = company

        with open(config_path, "w", encoding="utf-8") as configfile:
            config_parser.write(configfile)

# === VARIABLES === #
mot_de_passe = "e559bb3424a39d56e04456733d960020f4771e7c4eda548fbb793eba97c80ad9"
key = generate_key(mot_de_passe)

CONFIG_PATH = "config.ini"
ensure_general_section(CONFIG_PATH)
config = decrypt_ini(CONFIG_PATH, key)

INFLUX_URL = config["influxdb"]["url"]
INFLUX_TOKEN = config["influxdb"]["token"]
INFLUX_ORG = config["influxdb"]["org"]
INFLUX_BUCKET = config["influxdb"]["bucket"]

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

LOG_FILE = "agent.log"
ICON_PATHS = {
    "running": "./images/logo_monitoring.png",
    "paused": "./images/logo_monitoring_pause.png",
    "error": "./images/logo_monitoring_broke.png"
}

running = True
current_status = "running"
icon = None

# === LOGGING === #
def log(msg, important=True):
    """
    Ajoute une ligne dans le fichier log si le message est important.
    """
    if not important:
        return
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

# === DONNEES SYSTEME === #
def collect_all_data():
    """
    Collecte toutes les métriques système disponibles via les modules dédiés + trafic réseau.

    Returns:
        dict: Données système horodatées
    """
    try:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": system_info.get_data(),
            "cpu": cpu_info.get_data(),
            "memory": ram_info.get_data(),
            "disk": disk_info.get_data(),
            "updates": windows_update.get_data(),
            "network": network_info.get_data(),
        }
    except Exception as e:
        return {"error": f"Data collection failed: {str(e)}"}

def send_to_influx(data):
    """
    Envoie les données collectées dans la base InfluxDB avec les bons tags.
    - host : depuis config ou hostname système
    - company : nom d'entreprise fourni par l'utilisateur
    """
    config_name = config["general"].get("name", "").strip()
    hostname = config_name if config_name else data["system"].get("hostname", "unknown")
    company = config["general"].get("company", "unknown")

    measurement = "pc"
    records = []

    for metric in ["system", "cpu", "memory", "disk", "updates", "network"]:
        if metric not in data:
            continue
        for field_name, field_value in data[metric].items():
            if isinstance(field_value, (int, float)):
                point = (
                    Point(measurement)
                    .tag("host", hostname)
                    .tag("company", company)
                    .tag("metric", metric)
                    .field(field_name, field_value)
                )
                records.append(point)

    if records:
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=records)

# === ICON DYNAMIQUE === #
def update_icon(state):
    """
    Change dynamiquement l'icône affichée dans la barre système.
    """
    global current_status, icon
    if state == current_status:
        return
    try:
        new_icon = Image.open(ICON_PATHS[state])
        icon.icon = new_icon
        current_status = state
    except Exception as e:
        log(f"Erreur changement d'icône ({state}): {e}")

# === FONCTIONS SYSTRAY === #
def on_toggle_run(icon_obj, item):
    """
    Active ou désactive la collecte de données via clic sur l’icône.
    """
    global running
    running = not running
    log("▶ Agent repris." if running else "⏸ Agent en pause.")
    update_icon("running" if running else "paused")

def on_open_log(icon_obj, item):
    """Ouvre le fichier de log dans le visualiseur de fichiers."""
    os.startfile(LOG_FILE)

def on_quit(icon_obj, item):
    """Arrête complètement l'agent de surveillance."""
    log("Arrêt manuel de l'agent.")
    icon_obj.stop()
    os._exit(0)

def setup_tray():
    """
    Crée l'icône système avec menu interactif (pause, logs, quitter).
    """
    global icon
    image = Image.open(ICON_PATHS["running"])
    icon = Icon("agent_monitoring", image, "Agent de Monitoring", menu=Menu(
        MenuItem("⏯ Démarrer / Pause", on_toggle_run),
        MenuItem("📂 Ouvrir le fichier log", on_open_log),
        MenuItem("❌ Quitter", on_quit)
    ))
    icon.run()

# === THREAD PRINCIPAL === #
def main_loop():
    """
    Boucle principale de collecte de données toutes les 10 secondes.
    Envoie vers InfluxDB si actif, met à jour l’icône en fonction de l’état.
    """
    while True:
        try:
            if running:
                data = collect_all_data()
                send_to_influx(data)
                update_icon("running")
            else:
                update_icon("paused")
        except Exception as e:
            log(f"❌ Erreur boucle principale : {e}")
            update_icon("error")
        time.sleep(10)

if __name__ == "__main__":
    log("Agent démarré.")
    threading.Thread(target=main_loop, daemon=True).start()
    setup_tray()

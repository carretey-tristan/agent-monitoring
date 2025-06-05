"""
Module d'information système de base
------------------------------------
Ce module fournit des informations système générales :
- Nom d'hôte (hostname)
- Durée d'activité (uptime)

Utilise les bibliothèques standard `socket`, `datetime` et `psutil`.
"""

import socket
import psutil
from datetime import datetime

def get_data():
    """
    Récupère le nom de la machine et son uptime (durée depuis le dernier démarrage).

    Returns:
        dict: Dictionnaire contenant :
            - hostname (str) : Nom d'hôte de la machine
            - uptime_minutes (float) : Temps d'activité en minutes
            - error (str, optionnel) : Message d'erreur en cas de problème
    """
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        return {
            "hostname": socket.gethostname(),
            "uptime_minutes": uptime.total_seconds() // 60
        }
    except Exception as e:
        return {"error": f"Error in system_info: {str(e)}"}

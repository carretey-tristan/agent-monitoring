"""
Module de surveillance du disque
-------------------------------
Ce module fournit des informations sur l'utilisation du disque principal :
- Espace total
- Espace libre
- Pourcentage d'utilisation

Utilise la bibliothèque psutil pour accéder aux statistiques de disque.
"""

import psutil

def get_data():
    """
    Récupère les informations d'utilisation du disque principal (monté sur '/').
    
    Returns:
        dict: Dictionnaire contenant :
            - disk_total (int) : Espace total du disque en octets
            - disk_free (int) : Espace libre disponible en octets
            - disk_percent (float) : Pourcentage d'utilisation du disque
            - error (str, optionnel) : Message d'erreur en cas d'échec
    """
    try:
        disk = psutil.disk_usage('/')
        return {
            "disk_total": disk.total,
            "disk_free": disk.free,
            "disk_percent": disk.percent
        }
    except Exception as e:
        return {"error": f"Error in disk_info: {str(e)}"}

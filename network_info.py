import psutil

def get_data():
    """
    Récupère le trafic réseau total (toutes interfaces confondues).

    Returns:
        dict: 
            - bytes_sent (int): Nombre total d'octets envoyés
            - bytes_recv (int): Nombre total d'octets reçus
    """
    try:
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv
        }
    except Exception as e:
        return {"error": f"Network info error: {str(e)}"}

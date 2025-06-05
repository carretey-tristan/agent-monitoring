"""
Module de déchiffrement du fichier de configuration INI
--------------------------------------------------------
Ce module permet de transformer un fichier INI chiffré en une version lisible.

Fonctionnalités :
- Génère une clé à partir d'un mot de passe (SHA-256 + base64)
- Déchiffre les champs chiffrés dans les sections (sauf 'general')
- Écrit un nouveau fichier INI en clair

Utilise les bibliothèques cryptography et configparser.
"""

import configparser
from cryptography.fernet import Fernet
import base64
import hashlib

def generate_key(password: str) -> bytes:
    """
    Génère une clé Fernet à partir d'un mot de passe.

    Args:
        password (str): Le mot de passe brut.

    Returns:
        bytes: Clé compatible Fernet (base64, 256 bits).
    """
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def decrypt_ini_file(file_path: str, key: bytes, output_path: str = None):
    """
    Déchiffre les valeurs d'un fichier INI (hors section [general]) 
    et les écrit dans un nouveau fichier lisible.

    Args:
        file_path (str): Chemin du fichier INI chiffré.
        key (bytes): Clé Fernet pour le déchiffrement.
        output_path (str, optional): Chemin de sortie du fichier déchiffré. 
                                     Si non spécifié, crée 'config_dechiffre.ini'.
    """
    config = configparser.ConfigParser()
    config.read(file_path)
    fernet = Fernet(key)

    for section in config.sections():
        if section == "general":
            continue  # Cette section n'est pas chiffrée
        for option in config[section]:
            try:
                decrypted = fernet.decrypt(config[section][option].encode()).decode()
                config[section][option] = decrypted
            except Exception as e:
                print(f"Erreur de déchiffrement [{section}]->{option}: {e}")

    with open(output_path or "config_dechiffre.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)
    print(f"Fichier INI déchiffré : {output_path or 'config_dechiffre.ini'}")

# Exemple d'utilisation
if __name__ == "__main__":
    mot_de_passe = "e559bb3424a39d56e04456733d960020f4771e7c4eda548fbb793eba97c80ad9"
    key = generate_key(mot_de_passe)
    decrypt_ini_file("config.ini", key)

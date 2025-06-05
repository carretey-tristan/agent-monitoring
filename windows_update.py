"""
Module de vérification des mises à jour Windows
-----------------------------------------------
Ce module interroge le système pour connaître le nombre de mises à jour Windows disponibles (non installées).

Utilise PowerShell via `subprocess` pour accéder au COM Microsoft.Update.Session.
"""

import subprocess

def get_data():
    """
    Exécute une commande PowerShell pour récupérer le nombre de mises à jour Windows disponibles.

    Returns:
        dict: Dictionnaire contenant :
            - pending_updates (int) : Nombre de mises à jour logicielles non installées
            - error (str, optionnel) : Message d'erreur en cas de problème
    """
    try:
        result = subprocess.run(
            ["powershell", "-Command", """
            $Session = New-Object -ComObject Microsoft.Update.Session
            $Searcher = $Session.CreateUpdateSearcher()
            $Results = $Searcher.Search("IsInstalled=0 and Type='Software'")
            $Results.Updates.Count
            """],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW  # Cache la fenêtre PowerShell
        )
        output = result.stdout.strip()
        count = int(output) if output.isdigit() else 0
        return {"pending_updates": count}
    except Exception as e:
        return {"error": f"Windows Update check failed: {str(e)}"}

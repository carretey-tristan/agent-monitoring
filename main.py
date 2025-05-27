
import cpu_info
import ram_info
import disk_info
import os_info
from json import dumps
from datetime import datetime

MODULES = [
    ('cpu', cpu_info.get_cpu_info),
    ('ram', ram_info.get_ram_info),
    ('disk', disk_info.get_disk_info),
    ('os', os_info.get_os_info),
]

def print_metrics(measurement, metrics: dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")   
    print(f"\n=== {measurement} - {timestamp} ===")
    print("Métriques:", dumps(metrics, indent=2))
    print("=" * 50)

for measurement, func in MODULES:
    try:
        metrics = func()
        print_metrics(measurement, metrics)
    except Exception as e:
        print(f"Erreur lors de la collecte pour {measurement}: {e}")
input("\nAppuyez sur Entrée pour quitter...")

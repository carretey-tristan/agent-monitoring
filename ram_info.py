from psutil import virtual_memory

def get_ram_info():
    mem = virtual_memory()
    return {
        'ram_total_mb': round(mem.total / 1024 / 1024, 2),
        'ram_used_mb': round(mem.used / 1024 / 1024, 2),
        'ram_percent': mem.percent
    } 
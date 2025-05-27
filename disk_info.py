from psutil import disk_usage

def get_disk_info():
    disk = disk_usage('C:')
    return {
        'disk_total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
        'disk_used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
        'disk_percent': disk.percent
    } 
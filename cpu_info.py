from psutil import cpu_percent
def get_cpu_info():
    return {'cpu_percent': cpu_percent(interval=1)} 
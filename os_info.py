from platform import system,version
from socket import gethostname

def get_os_info():
    return {
        'hostname': gethostname(),
        'os': system(),
        'os_version': version()
    } 
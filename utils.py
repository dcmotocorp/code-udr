
import platform
import os
import socket

def shutdown_computer():
    """
    Shut down pc
    """
    system_type = platform.system()
    if system_type == "Windows":
        os.system("shutdown /s /t 1")
    elif system_type == "macOS":
        os.system("sudo shutdown -h now")
    elif system_type == "Linux":
        os.system("sudo shutdown -P now")
    else:
        print("Unsupported operating system")


def restart_computer():
    system_type = platform.system()
    if system_type == "Windows":
        os.system("shutdown /r /t 1")
    elif system_type == "Linux":
        os.system("sudo shutdown -r now")
    elif system_type == "Darwin":  # For macOS
        os.system("sudo shutdown -r now")
    else:
        print("Unsupported operating system")




def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except socket.error as e:
        print("Error:", e)
        return None

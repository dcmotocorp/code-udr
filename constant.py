import os 

script_path = os.path.abspath(__file__)
root_directory = os.path.dirname(script_path)
db_location = os.path.join(root_directory,"user_database.db")
db_directory = root_directory


SYSTEM_CONFIG_LABEL = "System Configuration :"
PASSWORD_LABEL = "Password:  ["
USERNAME_LABEL = "username"
NOVAIGU_LABEL = "Novaigu UDR 1.0.0"
NOVAIGU_PLATFORM_LABEL ="Mission Guard Platform"
NOVAIGU_HTTP_LABEL ="https://{}:3000"
F2_CONFIGURATION_SYSTEM = "<F2> Configuration System"
SHUT_DOWN_RESTART = "Shut Down/Restart"
F2_SHUT_DOWN= "<F2> Shut down"
F11_RESTART = "<F11> Restart"
ESC_CANCLE =  "<Esc> Cancle"
KEY_ESC = "esc"
KEY_DOWN = "down"
KEY_UP = "up"
AUTHENTICATION_SCREEN = 'authentication_screen'
PASSWORD = "Password"
HOSTNAME = "Hostname"
MANAGEMENT_INTERFACE = "Management Interface"
SSH = "SSH"
LOCK_DOWN_MODE = "Lock Mode"
RESET_SYSTEM_CONFIG = "Reset System Configuration"
NETWORK_ADAPTOR = "Network Adapter"
IP_CONFIGURATION = "IP Configuration"
DNS_SERVER = "DNS Servers"
SELECT_MANAGEMENT_NETWORK_SERVICE = "Select Management Network Adaptor"
CONFIGURE_MANAGEMENT_NETWORK_SERVICE = "Configure Management Network Adaptor"
OBTAIN_IP_AUTOMATIC = "Obtain IP address Automatically"
MANUALLY_IP_AUTOMATIC = "Manual IP Configuration"
CONFIGURE_DNS_SERVER = "Configure DNS Server"
OBTAIN_DNS_AUTOMATIC = "Obtain DNS server address Automatically"
MANUALLY_DNS_AUTOMATIC = "Manual DNS Configuration"
CONFIGURE_MANAGEMENT_INTERFACE = "Configure Management Interface"
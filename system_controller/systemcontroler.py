import subprocess
import platform
import psutil
import spwd
import crypt
import pam
import re
import docker
import socket
import netifaces
import time
import os
import spwd
from pyroute2 import IPRoute
from logs.udr_logger import UdrLogger
import subprocess

class SystemControler:
    def __init__(self) -> None:
        self.logger_ = UdrLogger()
        

    
    
    
    
    def authenticate(self, username, password):
        try:
            # Get the encrypted password hash from /etc/shadow
            encrypted_password = spwd.getspnam(username).sp_pwd
            # Verify the password
            response = crypt.crypt(password, encrypted_password) == encrypted_password
            self.logger_.log_info("Response of authentication {} = {} == {}".format(response,username, password))
            return response
            
        except KeyError as ex:
            # User not found
            self.logger_.log_info("Error of authentication{}".format(str(ex)))
            return False

    def get_default_interface(self):
        try:
            result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
            output = result.stdout.strip()
            match = re.search(r'default via \S+ dev (\S+)', output)
            if match:
                return match.group(1)
            else:
                return None
        except subprocess.CalledProcessError as e:
            pass 
            return None


        
    def change_password(self, user_name, old_password=None, new_password=None):
        try:
            # Prepare the command to change the password using chpasswd
            command = f"echo '{user_name}:{new_password}' | sudo chpasswd"

            # Execute the command
            os.system(command)
            return True
        except Exception as e:
            pass 
            return False

        
    def get_ip_address(self):
        interface = self.get_default_interface()
        if interface:
            with IPRoute() as ipr:
                addresses = ipr.get_addr(label=interface, family=2)
                if addresses:
                    return addresses[0].get_attr('IFA_ADDRESS')
        system_platform = platform.system()

        if system_platform == 'Windows':
            try:
                result = subprocess.check_output(['ipconfig']).decode('utf-8')
                ipv4_addresses = re.findall(r'IPv4 Address[^\d]+(\d+\.\d+\.\d+\.\d+)', result)
                ipv4_addresses = [ip for ip in ipv4_addresses if ip != '127.0.0.1']
                return ipv4_addresses[0]
            except subprocess.CalledProcessError:
                return "127.0.0.1"
        elif system_platform == 'Linux':
            try:
                result = subprocess.check_output(['ip', 'addr', 'show']).decode('utf-8')
                ipv4_addresses = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', result)
                ipv4_addresses = [ip for ip in ipv4_addresses if ip != '127.0.0.1']
                return ipv4_addresses[0]
            except subprocess.CalledProcessError:
                return "127.0.0.1"
            except Exception as e:
                return "127.0.0.1"
        else:
            return "127.0.0.1"
    
    def get_network_info_su_de(self):
        system_platform = platform.system()

        if system_platform == 'Windows':
            try:
                result = subprocess.check_output(['ipconfig', '/all']).decode('utf-8')
                ipv4_address_match = re.search(r'IPv4 Address[^\d]+(\d+\.\d+\.\d+\.\d+)', result)
                ipv4_address = ipv4_address_match.group(1) if ipv4_address_match else '127.0.0.1'

                subnet_mask_match = re.search(r'Subnet Mask[^\d]+(\d+\.\d+\.\d+\.\d+)', result)
                subnet_mask = subnet_mask_match.group(1) if subnet_mask_match else '255.255.255.0'

                default_gateway_match = re.search(r'Default Gateway[^\d]+(\d+\.\d+\.\d+\.\d+)', result)
                default_gateway = default_gateway_match.group(1) if default_gateway_match else 'Not found'

                return ipv4_address, subnet_mask, default_gateway
            except subprocess.CalledProcessError:
                return "127.0.0.1", "255.255.255.0", "Not found"
        elif system_platform == 'Linux':
            try:
                result = subprocess.check_output(['ip', 'route', 'show']).decode('utf-8')
                default_gateway_match = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', result)
                default_gateway = default_gateway_match.group(1) if default_gateway_match else 'Not found'

                return self.get_ip_address(), "255.255.255.0", default_gateway
            except subprocess.CalledProcessError:
                return "127.0.0.1", "255.255.255.0", "Not found"
        else:
            return "127.0.0.1", "255.255.255.0", "Not found"

    def shutdown_system(self):
        system_type = platform.system()
        if system_type == "Windows":
            os.system("shutdown /s /t 1")
        elif system_type == "macOS":
            os.system("sudo shutdown -h now")
        elif system_type == "Linux":
            os.system("sudo shutdown -P now")
        else:
            pass 

    def restart_computer(self):
        system_type = platform.system()
        if system_type == "Windows":
            os.system("shutdown /r /t 1")
        elif system_type == "Linux":
            os.system("sudo shutdown -r now")
        elif system_type == "Darwin":  # For macOS
            os.system("sudo shutdown -r now")
        else:
            pass 

    def set_dns_configuration_linux(self,primary_dns, secondary_dns):
        try:
            # Use sudo to write to /etc/resolv.conf
            command = f"echo 'nameserver {primary_dns}\nnameserver {secondary_dns}' | sudo tee /etc/resolv.conf > /dev/null"
            subprocess.run(command, shell=True, check=True)
            return True, "DNS configuration updated successfully."
        except subprocess.CalledProcessError as e:
            return False, "Error DNS configuration updated."
        
    def get_connection_name(self, interface):
        try:
            # Execute the nmcli command to get connection information
            result = subprocess.run(['nmcli', '-t', '-f', 'NAME,DEVICE', 'connection', 'show', '--active'], capture_output=True, text=True, check=True)
            output = result.stdout.strip()

            # Parse the output to find the connection name associated with the interface
            lines = output.split('\n')
            for line in lines:
                parts = line.split(':')
                if len(parts) == 2 and parts[1] == interface:
                    connection_name = parts[0].strip()
                    return connection_name

            # If no connection name is found
            return None

        except subprocess.CalledProcessError as e:
            return None
        
    def set_dns_configuration_manually_linux(self,primary_dns, secondary_dns):
        try:
            
            interface = self.get_default_interface()
            if not interface:
                return False
            connection_name = self.get_connection_name(interface=interface)

            # Construct the command based on whether secondary DNS is provided
            # if secondary_dns:
            #     dns_command = f"{primary_dns},{secondary_dns}"
            # else:
            #     dns_command = primary_dns

            # Convert the list of DNS servers into a comma-separated string
            dns = f"{primary_dns},{secondary_dns}"

            # Set the DNS servers
            subprocess.run(["nmcli", "con", "mod", connection_name, "ipv4.dns", dns], check=True)

            # To ensure the changes take effect, reactivate the connection
            subprocess.run(["nmcli", "con", "down", connection_name], check=True)
            subprocess.run(["nmcli", "con", "up", connection_name], check=True)

            # dns_servers = [primary_dns, secondary_dns]
            # with open(f"/etc/resolv_{interface}.conf", "w") as f:
            #     for dns_server in dns_servers:
            #         f.write(f"nameserver {dns_server}\n")
            return True, "DNS configuration updated successfully."
        except subprocess.CalledProcessError as e:
            return False, "Error DNS configuration updated."
        
    def get_dns_configuration_linux(self):
        try:
            interface = self.get_default_interface()
            result = subprocess.run(['nmcli', '-g', 'IP4.DNS', 'device', 'show', interface], capture_output=True, text=True, check=True)
            output = result.stdout.strip()

            # Split the output by '|' and strip whitespace
            dns_servers = [dns.strip() for dns in output.split('|')]

            # Extract primary and secondary DNS servers
            primary_dns = dns_servers[0]
            secondary_dns = dns_servers[1] if len(dns_servers) > 1 else None
            self.logger_.log_info(" primary secondarye in {}  {}".format(primary_dns,secondary_dns))  
            return primary_dns,secondary_dns
        except FileNotFoundError:
            self.logger_.log_info(" file not occure in {}".format(str(e)))
            return "", ""
        except Exception as e:
            self.logger_.log_info(" exception occure in {}".format(str(e)))
            return "", ""
        
        

    def reset_dns_configuration_linux(self):
        try:
            # Use sudo to write to /etc/resolv.conf
            command = "echo '' | sudo tee /etc/resolv.conf > /dev/null"
            subprocess.run(command, shell=True, check=True)
            return True, "DNS configuration reset to default successfully."
        except subprocess.CalledProcessError as e:
            return False, "Error DNS configuration reset to default."
        
    def auto_dns_configuration_linux(self):
        try:
            # {'Match': {'Name': 'wlp0s20f3'}, 'Network': {'Address': '10.5.51.244', 'Gateway': '10.5.50.1', 'DNS': '10.5.50.1', 'Mask': '255.255.254.0'}}
            config = self.read_network_config()
            if 'Match' not in config:
                return False, "Please set management interface first."
            if 'DHCP' in config:
                auto_dns = self.return_auto_dns_config(config['Match']['Name'], auto_ip=True)
            else:
                auto_dns = self.return_auto_dns_config(config['Match']['Name'], 
                                                       address=config['Network']['Address'], 
                                                       gateway=config['Network']['Gateway'], 
                                                       mask=config['Network']['Mask'], auto_ip=False)
            self.create_network_file("mgmt", auto_dns)
            self.create_network_file(config['Match']['Name'], auto_dns)
            subprocess.run(["systemctl", "restart", "systemd-networkd"])
            return True, "DNS configuration reset to default successfully."
        except subprocess.CalledProcessError as e:
            return False, "Error DNS configuration reset to default."

    def stop_all_containers(self):
        try:
            client = docker.from_env()
            containers = client.containers.list()

            for container in containers:
                container.stop()
        except Exception as e:
            pass 

    def enable_lockdown_mode(self, user_name=None):
        try:
            # Disable all network interfaces
            # interface = self.get_default_interface()
            
            # self.reset_ip_down_interface(interface=interface)
            # subprocess.run(["sudo", "ip", "link", "set", interface, "down"])

            # Save iptables rules to a file
            # subprocess.run(["sudo", "iptables-save"], stdout=subprocess.PIPE, check=True, text=True, input="").stdout > "/etc/iptables/rules.v4"

            # Disable outgoing traffic
            # subprocess.run(["sudo", "iptables", "-A", "OUTPUT", "-j", "DROP"])

            # Disable SSH
            subprocess.run(["sudo", "service", "ssh", "stop"])

            # Disable all user accounts except root
            # users = self.get_all_users()
            # root_users = self.get_root_users(users=users)
            # for user in users:
            #     if user not in root_users:
            #         subprocess.run(["sudo", "chpasswd"], input=f"{user}:Xadmin@123\n", universal_newlines=True)
            #         subprocess.run(["sudo", "passwd", "-l", user])


        except Exception as e:
            pass 

    def exit_lockdown_mode(self):
        try:
            # Load iptables rules from the file
            # subprocess.run(["sudo", "iptables-restore", "-c", "/etc/iptables/rules.v4"])

            # Enable all network interfaces
            # interface= self.get_default_interface()
        
            # subprocess.run(["sudo", "ip", "link", "set", interface, "up"])

            # Enable outgoing traffic
            # subprocess.run(["sudo", "iptables", "-D", "OUTPUT", "-j", "DROP"])

            # Enable SSH
            subprocess.run(["sudo", "service", "ssh", "start"])

        except Exception as ex:
            self.logger_.log_info("Exception occure in exit lock down {}".format(str(ex)))
            pass 
    
    def lock_screen_linux(self):
        subprocess.run(["xdg-screensaver", "lock"])

    def is_root_user(self, user):
        try:
            result = subprocess.run(["id", "-u", user], stdout=subprocess.PIPE, check=True)
            uid = int(result.stdout.decode())
            return uid == 0
        except Exception as e:
            return False
    
    def get_root_users(self, users):
        try:
            # Check if each user is the root user
            root_users = [user for user in users if self.is_root_user(user)]
            
            return root_users

        except Exception as e:
            
            return []

    def get_all_users(self):
        try:
            result = subprocess.run(["cut", "-d:", "-f1", "/etc/passwd"], stdout=subprocess.PIPE, check=True)
            users = result.stdout.decode().split("\n")[:-1]  # Remove the empty last element
            return users

        except Exception as e:
           
            return []

    def get_all_network_interfaces(self):
        try:
            result = subprocess.run(["ip", "link", "show"], stdout=subprocess.PIPE, check=True)
            interfaces = [line.split(":")[1].strip() for line in result.stdout.decode().split('\n') if line.startswith(' ') and ':' in line]
          
            return interfaces
        except Exception as e:
            return []
    



    def enable_ssh(self):
        try:
            subprocess.run(["sudo", "systemctl", "enable", "ssh"], stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "systemctl", "start", "ssh"], stderr=subprocess.DEVNULL)
        except Exception as ex:
            self.logger_.log_info("Exception occurred while cleaning enable screen: {}".format(str(ex)))
    
    def disable_ssh(self):
        try:
            subprocess.run(["sudo", "systemctl", "stop", "ssh"], stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "systemctl", "disable", "ssh"], stderr=subprocess.DEVNULL)
        except Exception as ex:
            self.logger_.log_info("Exception occurred while cleaning disable screen: {}".format(str(ex)))

    def start_all_containers(self):
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)

            for container in containers:
                container.start()
        except Exception as e:
            pass 

    def get_hostname(self):
        try:
            # Get the hostname
            hostname = socket.gethostname()
            return hostname
        except Exception as e:
            return None
        
    def set_hostname(self, new_hostname):
        try:
            self.update_hosts_file(socket.gethostname(), new_hostname)

            # Run the hostnamectl command to set the new hostname

            self.logger_.log_info("host name value in controller {} type {}".format(new_hostname,type(new_hostname)))
            subprocess.run(['sudo', 'hostnamectl', 'set-hostname', str(new_hostname)], check=True)
            
            return True, "host name changed"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {str(e)}"
    
    def update_hosts_file(self, hostname, new_hostname):
        try:
            # Update /etc/hosts file
            with open('/etc/hosts', 'r') as f:
                lines = f.readlines()
            
            # Find and replace the old hostname with the new one
            new_lines = []
            for line in lines:
                if hostname in line:
                    line = line.replace(hostname, new_hostname)
                new_lines.append(line)

            # Write back the updated lines to the file
            with open('/etc/hosts', 'w') as f:
                f.writelines(new_lines)

        except Exception as e:
            pass 
        
    def reset_network_config(self):
        try:
            # Reset network configurations to use DHCP
            subprocess.run(['sudo', 'dhclient', '-r'])  # Release current IP address
            subprocess.run(['sudo', 'dhclient'])  # Obtain new IP address using DHCP
            return True, "Network configuration reset successfully."
        except subprocess.CalledProcessError as e:
            return False, "Failed to reset network configuration."
        
    def reset_network_file(self, interface):
        try:
            with open('/etc/network/interfaces', 'r') as config_file:
                existing_config = config_file.readlines()

                unique_identifier = f"# Interface: {interface}\n"
        
        
            interface_found = False
            updated = 0
            for i, line in enumerate(existing_config):
                if line.strip() == unique_identifier.strip():
                    interface_found = True
                    existing_config[i] = ""
                elif interface_found and updated == 0:
                    updated += 1
                    existing_config[i] = ""
                elif interface_found and updated == 1:
                    updated += 1
                    existing_config[i] = ""
                elif interface_found and updated == 2:
                    updated += 1
                    existing_config[i] = ""
                elif interface_found and updated == 3:
                    updated += 1
                    existing_config[i] = ""
                elif interface_found and updated == 4:
                    updated += 1
                    existing_config[i] = ""
                elif interface_found and updated == 5:
                    updated += 1
                    existing_config[i] = ""
            
            
            
            # Write the modified content back to the file
            with open('/etc/network/interfaces', 'w') as config_file:
                config_file.writelines(existing_config)

            self.reset_ip_down_interface(interface=interface)
            self.reset_ip_up_interface(interface=interface)
            # Restart NetworkManager service
            subprocess.run(['sudo', 'systemctl', 'restart', 'NetworkManager'], check=True)
        except Exception as e:
            pass 

    def reset_ip_config(self):
        try:
            interface = self.get_default_interface()
            if not interface:
                return False
            # Release the DHCP lease
            subprocess.run(['sudo', 'dhclient', '-r', interface], check=True)
            # Flush the IP address configuration
            subprocess.run(['sudo', 'ip', 'addr', 'flush', 'dev', interface], check=True)
            # Request a new DHCP lease
            subprocess.run(['sudo', 'dhclient', interface], check=True)
            subprocess.run(['sudo', 'systemctl', 'restart', 'NetworkManager'], check=True)

            return True, "Network interface reset successfully."
        except subprocess.CalledProcessError as e:

            return False, f"Error occurred: {e}"

        
    def get_default_interface(self):
        # Get a list of all network interfaces
        interfaces = netifaces.interfaces()

        # Iterate over each interface to find the default one
        for interface in interfaces:
            # Check if the interface is not a loopback interface and has an IP address assigned
            if interface != 'lo' and netifaces.AF_INET in netifaces.ifaddresses(interface):
                return interface

        return None  # Return None if no default interface is found

    def get_current_ip(self, interface):
        # Get the list of addresses assigned to the specified interface
        addresses = netifaces.ifaddresses(interface).get(netifaces.AF_INET)

        if addresses:
            # Return the first IP address in the list
            return addresses[0]['addr']

        return None  # Return None if no IP address is found for the interface

    def set_ip_configuration(self, ip_address, subnet_mask, default_gateway):
        try:
            # Get the default network interface
            interface = self.get_default_interface()
            if not interface:
                return "Error: Cannot find the default network interface."

            # Check if an IP address is already assigned to the interface
            existing_ip = self.get_current_ip(interface)
            if existing_ip:
                # Remove the existing IP address
                subprocess.run(['sudo', 'ip', 'addr', 'del', existing_ip, 'dev', interface], check=True)
            
            time.sleep(1)

            # Set IP address and subnet mask using ip command
            subprocess.run(['sudo', 'ip', 'addr', 'add', f'{ip_address}/{subnet_mask}', 'dev', interface], check=True)
            time.sleep(1)

            # Set default gateway using ip command
            subprocess.run(['sudo', 'ip', 'route', 'add', 'default', 'via', default_gateway], check=True)

            return True, "IP configuration set successfully."
        except subprocess.CalledProcessError as e:
            self.reset_network_config()

            return False, f"Error: while updating the IP Automatically"
    
    def reset_network_configuration(self):
        try:
            interface = self.get_default_interface()
            # Remove manually assigned IP address and subnet mask
            subprocess.run(["sudo", "ip", "addr", "flush", "dev", interface], check=True)
            
            # Remove default route
            subprocess.run(["sudo", "ip", "route", "flush", "dev", interface], check=True)
            
            return True, "Network configuration reset successfully."
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"

    def set_dns_auto_assign(self):
        try:
            interface = self.get_default_interface()
            if not interface :
                return False
            connection_name = self.get_connection_name(interface)

            # Clear the custom DNS settings to revert to obtaining DNS automatically
            subprocess.run(["nmcli", "con", "mod", connection_name, "ipv4.ignore-auto-dns", "no", "ipv4.dns", ""], check=True,stderr=subprocess.DEVNULL)

            # Reactivate the connection to apply changes
            subprocess.run(["nmcli", "con", "down", connection_name], check=True,stderr=subprocess.DEVNULL)
            subprocess.run(["nmcli", "con", "up", connection_name], check=True,stderr=subprocess.DEVNULL)

            
            return True, "DNS configuration set to auto-assign successfully."
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
        
    def subnet_mask_to_cidr(self, subnet_mask):
        # Convert subnet mask to CIDR notation
        mask_octets = subnet_mask.split('.')
        binary_str = ''.join([bin(int(octet)).lstrip('0b').rjust(8, '0') for octet in mask_octets])
        cidr = binary_str.count('1')
        return cidr
    
    def reset_ip_down_interface(self, interface):
        try:
            subprocess.run(['sudo', 'ifdown', interface], check=True)
        except Exception as e:
            pass 
    
    def reset_ip_up_interface(self, interface):
        try:
            subprocess.run(['sudo', 'ifup', interface], check=True)
        except Exception as e:
            pass 

    def convert_subnet_mask_to_cidr(self, subnet_mask):
        """
        Convert a subnet mask from dot-decimal notation to CIDR notation.

        Parameters:
        - subnet_mask (str): The subnet mask in dot-decimal notation.

        Returns:
        - int: The CIDR notation of the subnet mask.
        """
        return sum([bin(int(x)).count('1') for x in subnet_mask.split('.')])
    
    def set_ip_configuration_manual(self, ip_address, subnet_mask, default_gateway):
        try:
            interface = self.get_default_interface()
            if not interface :
                return False
            connection_name = self.get_connection_name(interface=interface)
            # Check if the configuration already exists for the interface
            # Convert the subnet mask to CIDR notation
            cidr_subnet_mask = self.convert_subnet_mask_to_cidr(subnet_mask)

            # Set the IP address, subnet mask (in CIDR), and gateway
            subprocess.run(["nmcli", "con", "mod", connection_name,
                            "ipv4.addresses", f"{ip_address}/{cidr_subnet_mask}",
                            "ipv4.gateway", default_gateway,
                            "ipv4.method", "manual"],stderr=subprocess.DEVNULL)

            
            # Reactivate the connection to apply changes
            subprocess.run(["nmcli", "con", "down", connection_name],stderr=subprocess.DEVNULL)
            subprocess.run(["nmcli", "con", "up", connection_name],stderr=subprocess.DEVNULL)

            
            # # Bring up the interface
            
            
            return True, "IP configuration set successfully."
        except subprocess.CalledProcessError as e:
            self.reset_ip_config()
            return False, f"Error while updating the IP manually."
    
    def setup_ip_configuration(self, ip_address, subnet_mask, default_gateway):
        try:
            # Get the default network interface
            interface = self.get_default_interface()
            if not interface:
                return "Error: Cannot find the default network interface."

            # Check if an IP address is already assigned to the interface
            existing_ip = self.get_current_ip(interface)
            if existing_ip:
                # Remove the existing IP address
                subprocess.run(['sudo', 'ip', 'addr', 'del', existing_ip, 'dev', interface], check=True)
            
            time.sleep(1)

            # Set IP address and subnet mask using ip command
            subprocess.run(['sudo', 'ip', 'addr', 'add', f'{ip_address}/{subnet_mask}', 'dev', interface], check=True)
            time.sleep(1)

            # Set default gateway using ip command
            subprocess.run(['sudo', 'ip', 'route', 'add', 'default', 'via', default_gateway], check=True)

            return True, "IP configuration set successfully."
        except subprocess.CalledProcessError as e:
            self.reset_network_config()
            return False, f"Error: while updating the IP Automatically"
        
    def reset_dns_servers(self):
        try:
            output = subprocess.check_output(['nmcli', 'dev', 'show'])
            output = output.decode('utf-8').split('\n')
            dns_servers = []
            for line in output:
                if 'IP4.DNS' in line:
                    dns_servers.append(line.split(':')[-1].strip())
            if dns_servers:
                self.set_dns_servers(*dns_servers)
            else:
                pass 
                
        except subprocess.CalledProcessError as e:

            return []
    
    def set_dns_servers(self, primary_dns, secondary_dns):
        try:
            # Linux command to set DNS servers
            command = f"sudo nmcli connection modify 'Wired connection 1' ipv4.dns '{primary_dns} {secondary_dns}'"
            subprocess.run(command, shell=True)
        except subprocess.CalledProcessError as e:
            pass 
    
    def is_valid_ip(self, ip):
        # Regular expression pattern for matching an IP address
        ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        # Check if the given IP matches the pattern
        if re.match(ip_pattern, ip):
            return True
        else:
            return False
        
    def get_management_interface_name(self):
        mgmt_file_path = f"/etc/systemd/network/mgmt.network"
        if os.path.isfile(mgmt_file_path):
            with open(mgmt_file_path, 'r') as file:
                for line in file:
                    if line.startswith("Name="):
                        return line.strip().split("=")[1]
        return None
    
    def get_management_interface(self):
        mgmt_interface = self.get_default_interface()
        current_interface = None
        for interface, addrs in psutil.net_if_addrs().items():
            ipv4_addrs = [
                addr for addr in addrs if addr.family == socket.AF_INET]
            if ipv4_addrs:
                if interface != 'lo' and not interface.startswith('docker'):
                    current_interface = interface
                    if current_interface == mgmt_interface:
                        return interface, True
        return current_interface, False
    
    def get_dns(self, interface):
        primary_dns = secondary_dns = None
        try:
            # Run resolvectl dns command to get DNS information
            result = subprocess.run(['sudo', 'resolvectl', 'dns', interface], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                output = output.split(":")
                servers = output[-1].split(" ")
                ip_addresses = [ip.strip() for ip in servers if ip.strip() and ip.strip().count('.') == 3]
                if len(ip_addresses) >= 1:
                    primary_dns = ip_addresses[0]
                if len(ip_addresses) >= 2:
                    secondary_dns = ip_addresses[1]
            else:
                pass 
        except Exception as e:
            pass 
        return primary_dns, secondary_dns
    
    def convert_duplex_to_standard(self, speed_duplex):
        if speed_duplex == psutil.NIC_DUPLEX_FULL:
            return "Full"
        elif speed_duplex == psutil.NIC_DUPLEX_HALF:
            return "Half"
        else:
            return "Unknown"
    
    
    def get_interface_speed_and_duplex(self, interface_name):
        try:
            speed_file_path = f"/sys/class/net/{interface_name}/speed"
            duplex_file_path = f"/sys/class/net/{interface_name}/duplex"

            # Read speed and duplex information from files
            with open(speed_file_path, 'r') as speed_file, open(duplex_file_path, 'r') as duplex_file:
                speed = speed_file.read().strip() if speed_file else "Unknown"
                duplex = duplex_file.read().strip() if duplex_file else "Unknown"

            return speed, duplex
        except FileNotFoundError:
            return "Unknown", "Unknown"
        except Exception:
            return "Unknown", "Unknown"
        
    def get_default_interface(self):

        try:
            # Command to get the default route
            command = "ip route show default"
            
            # Execute the command
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse the output to extract the interface name
                output_lines = result.stdout.split('\n')
                if len(output_lines) > 0:
                    default_route_info = output_lines[0].split()
                    if len(default_route_info) > 4:
                        interface = default_route_info[4]
                        return interface
        except Exception as e:
            pass 
        return None
        
    def get_management_interface_details(self):
        management_interface, is_management = self.get_management_interface()
        all_interfaces = self.get_network_interfaces_and_state()
        if management_interface:
            interface_details = {"interface": management_interface, "is_management": True}  # Add interface name
            addresses = psutil.net_if_addrs().get(management_interface, [])
            for address in addresses:
                if address.family == psutil.AF_LINK:  # Check if it's a MAC address
                    interface_details["macAddress"] = address.address
                    break
            else:
                interface_details["macAddress"] = ""

            if_addrs = psutil.net_if_addrs().get(management_interface, [])
            interface_details["ipAddresses"] = [
                addr.address for addr in if_addrs if addr.family == socket.AF_INET]
            interface_details["subnetMasks"] = [
                addr.netmask for addr in if_addrs if addr.family == socket.AF_INET]

            try:
                primary_dns, secondary_dns = self.get_dns(management_interface)
                interface_details["primaryDns"] = primary_dns
                interface_details["secondaryDns"] = secondary_dns
            except (IndexError, KeyError):
                interface_details["primaryDns"] = interface_details["secondaryDns"] = ""

            try:
                speed, speed_duplex = self.get_interface_speed_and_duplex(management_interface)
                duplex_standard = self.convert_duplex_to_standard(speed_duplex)
            except KeyError:
                duplex_standard = speed = ""

            if psutil.net_if_stats().get(management_interface) is not None:
                if psutil.net_if_stats()[management_interface].isup:
                    interface_details["state"] = "Connected"
                    interface_details["status"] = "Enabled"
                else:
                    interface_details["state"] = "Disconnected"
                    interface_details["status"] = "Disabled"
            else:
                interface_details["state"] = ""
                # Assuming if there are no stats, interface is disabled
                interface_details["status"] = "Disabled"

            interface_details["interface"] = management_interface
            interface_details["speed"] = speed
            interface_details["duplex"] = duplex_standard
            all_interfaces.append(interface_details)

        return all_interfaces
    
    def get_default_gateway(self, interface):
        try:
            # Execute the command to get the default gateway
            result = subprocess.run(['ip', 'route', 'show', 'dev', interface], capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Parse the output to extract the default gateway
            default_gateway = None
            lines = output.split('\n')
            for line in lines:
                if 'default via' in line:
                    parts = line.split()
                    default_gateway = parts[2]
                    break
            
            return default_gateway

        except subprocess.CalledProcessError as e:
            return None
    
    def read_network_config(self):
        network_config_dict = {'Network': {}}
        try:
            interface = self.get_default_interface()
            # Get interface configuration
            result = subprocess.run(['sudo', 'ifconfig', interface], capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Parse IP address, subnet mask, and default gateway from the output
            ip_address = None
            subnet_mask = None
            default_gateway = None
            
            
            lines = output.split('\n')
            for line in lines:
                if 'inet ' in line:
                    parts = line.split()
                    ip_address = parts[1]
                    subnet_mask = parts[3].replace('Mask:', '')
                elif 'default via' in line:
                    parts = line.split()
                    default_gateway = parts[2]
             
            network_config_dict['Network']['Address'] = ip_address
            network_config_dict['Network']['Mask'] = subnet_mask
            network_config_dict['Network']['Gateway'] = self.get_default_gateway(interface=interface)

        except subprocess.CalledProcessError as e:
            pass 
        except Exception as e:
            pass 
        return network_config_dict
    
    def read_network_interface(self, interface):
        file_path = f"/etc/systemd/network/{interface}.network"
        network_config_dict = {}
        try:
            with open(file_path, "r") as file:
                section = None
                for line in file:
                    line = line.strip()
                    if not line:
                        continue  # Skip empty lines
                    if line.startswith("[") and line.endswith("]"):
                        section = line[1:-1]
                        network_config_dict[section] = {}
                    elif "=" in line and section:
                        key, value = line.split("=", 1)
                        network_config_dict[section][key.strip()] = value.strip()
        except Exception as e:
                pass 
        return network_config_dict
    
    def create_network_file(self, interface, network_config):
        # Define the file path
        file_path = f"/etc/systemd/network/{interface}.network"

        # Write the configuration to the file
        with open(file_path, "w") as file:
            file.write(network_config.strip())

    def update_network_config(self, interface, new_details):
        # Assuming interface is something like 'eth0' and new_details is a dictionary containing updated details
        config_file = f"/etc/network/interfaces.d/{interface}.cfg"  # Example path to network config file

        # Check if the file exists, create it if it doesn't
        if not os.path.exists(config_file):
            with open(config_file, 'w') as f:
                # Optionally, you can write default configuration here if needed
                pass

        # Open the config file, update the relevant details, and save the changes
        with open(config_file, 'r') as f:
            lines = f.readlines()
        with open(config_file, 'w') as f:
            for line in lines:
                # Modify lines as needed, for example, replacing old details with new ones
                if line.startswith('address'):
                    line = f"address {new_details['address']}\n"
                elif line.startswith('netmask'):
                    line = f"netmask {new_details['netmask']}\n"
                # Update other details similarly...

                f.write(line)

    def restart_network_service(self):
        # Command to restart networking service (for Debian-based systems)
        restart_command = ['sudo', 'systemctl', 'restart', 'networking']

        # Execute the command
        subprocess.run(restart_command, check=True)

    def get_network_infomation(self):
        network_info = {}

        # Get all network interfaces
        interfaces = netifaces.interfaces()

        # Get default gateway
        gateway_output = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
        gateway_info = gateway_output.stdout.split()
        gateway_ip = None
        for i, item in enumerate(gateway_info):
            if item == 'via':
                gateway_ip = gateway_info[i+1]
                break

        for interface in interfaces:
            interface_info = {}

            # Get IP address and subnet mask
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                ipv4_info = addrs[netifaces.AF_INET][0]
                interface_info['Address'] = ipv4_info['addr']
                interface_info['Mask'] = ipv4_info.get('netmask', '')

            # Add default gateway to each interface
            if gateway_ip:
                interface_info['Gateway'] = gateway_ip

            # Get DNS server
            dns_output = subprocess.run(['nmcli', 'dev', 'show', interface], capture_output=True, text=True)
            dns_lines = dns_output.stdout.split('\n')
            for line in dns_lines:
                if 'IP4.DNS' in line:
                    interface_info['DNS'] = line.split(':')[1].strip()
                    break

            # Add interface info to network_info if it has any information
            if interface_info:
                network_info[interface] = interface_info

        return network_info
    
    def return_auto_ip_config(self, interface, dns):
        if dns:
            default_config = f"""
        [Match]
Name={interface}

[Network]
DNS={dns}"""
        else:
            default_config = f"""
        [Match]
Name={interface}

[Network]"""
        return default_config
    
    def return_manual_ip_config(self, interface, dns, address, gateway, mask, auto_dns=False):
        if auto_dns:
            default_config = f"""
        [Match]
Name={interface}

[Network]
Address={address}
Gateway={gateway}
Mask={mask}"""
        else:
            default_config = f"""
        [Match]
Name={interface}

[Network]
Address={address}
Gateway={gateway}
DNS={dns}
Mask={mask}"""
        return default_config
    
    def return_auto_dns_config(self, interface, address=None, gateway=None, mask=None, auto_ip=False):
        if auto_ip:
            default_config = f"""
            [Match]
    Name={interface}

    [Network]
    """
        else:
            default_config = f"""
        [Match]
Name={interface}

[Network]
Address={address}
Gateway={gateway}
Mask={mask}"""
        return default_config
    
    def return_manual_dns_config(self, interface, dns, address=None, gateway=None, mask=None, auto_ip=False):
        if auto_ip:
            default_config = f"""
            [Match]
    Name={interface}

    [Network]
    DNS={dns}"""
        else:
            default_config = f"""
        [Match]
Name={interface}

[Network]
Address={address}
Gateway={gateway}
DNS={dns}
Mask={mask}"""
        return default_config
    
    def remove_existing_default_route(self):
        subprocess.run(['sudo', 'ip', 'route', 'del', 'default'])
        subprocess.run(['sudo', 'ip', 'route', 'flush', 'table main'])

    def apply_changes(self):
        subprocess.run(['sudo', 'netplan', 'apply'])
    
    def get_ipv4_address(self, interface):
        with IPRoute() as ipr:
            addresses = ipr.get_addr(label=interface, family=2)
            if addresses:
                return addresses[0].get_attr('IFA_ADDRESS')

    def set_management_interface(self, interface):
        try:
            ip_address = self.get_ipv4_address(interface=interface)
            if ip_address:
                with IPRoute() as ipr:
                    # Find the index of the specified interface
                    index = ipr.link_lookup(ifname=interface)[0]
                    
                    # Set the specified interface as the primary interface
                    ipr.link('set', index=index, state='up')
                    ipr.route('del', dst='default')
                    ipr.route('add', dst='default', gateway=ip_address)
        except Exception as e:
            return False, f"error {str(e)}"

        # Check if the command executed successfully
        
        return True, "Primary interface changed"
    
    def configure_management_ip(self, interface, ip, subnet, gateway):
        # Configure IP address and subnet mask
        subprocess.run(["sudo", "ip", "addr", "add", f"{ip}/{subnet}", "dev", interface])
        
        # Add default route
        subprocess.run(["sudo", "ip", "route", "add", "default", "via", gateway, "dev", interface])
        
    def get_network_interfaces_and_state(self):
        management_interface = self.get_default_interface()
        interfaces = psutil.net_if_addrs()
        interface_states = []

        for interface, addresses in interfaces.items():
            if interface == "lo":
                # Skip loopback interface and management interface
                continue

            is_virtual = False
            for address in addresses:
                if address.family == psutil.AF_LINK:  # Check if it's a MAC address
                    mac_address = address.address
                    break
            else:
                mac_address = ""

            if_addrs = psutil.net_if_addrs().get(interface, [])
            ip_addresses = [
                addr.address for addr in if_addrs if addr.family == socket.AF_INET]
            subnet_masks = [
                addr.netmask for addr in if_addrs if addr.family == socket.AF_INET]

            try:
                primary_dns, secondary_dns = self.get_dns(interface)
                # dns_servers = self.get_dns_servers_from_resolv_conf()
                # primary_dns = dns_servers[0] if dns_servers else ""
                # secondary_dns = dns_servers[1] if len(dns_servers) > 1 else ""
            except (IndexError, KeyError):
                primary_dns = secondary_dns = ""

            try:
                speed, speed_duplex = self.get_interface_speed_and_duplex(interface)
                duplex_standard = self.convert_duplex_to_standard(speed_duplex)
            except KeyError:
                duplex_standard = speed = ""

            if psutil.net_if_stats().get(interface) is None:
                is_virtual = True

            if not is_virtual:
                if interface in psutil.net_if_stats() and psutil.net_if_stats()[interface].isup:
                    state = "Connected"
                    enabled = "Enabled"
                else:
                    state = "Disconnected"
                    enabled = "Disabled"

                interface_states.append({
                    "interface": interface,
                    "state": state,
                    "macAddress": mac_address,
                    "ipAddresses": ip_addresses,
                    "subnetMasks": subnet_masks,
                    "primaryDns": primary_dns,
                    "secondaryDns": secondary_dns,
                    "speed": speed,
                    "status": str(enabled).upper(),
                    "duplex": duplex_standard, 
                    "is_management": True if management_interface and management_interface == interface else False
                })

        return interface_states
    
    def get_ipv4_address(self, interface):
        with IPRoute() as ipr:
            addresses = ipr.get_addr(label=interface, family=2)
            if addresses:
                return addresses[0].get_attr('IFA_ADDRESS')

    def set_management_interface(self, interface):
        try:
            subprocess.run(["sudo", "ip", "link", "set", interface, "up"])
            ip_address = self.get_ipv4_address(interface=interface)
            print(ip_address)
            if ip_address:
                with IPRoute() as ipr:
                    # Find the index of the specified interface
                    index = ipr.link_lookup(ifname=interface)[0]
                    print(f"this is index {index}")

                    # Set the specified interface as the primary interface
                    ipr.link('set', index=index, state='up')
                    ipr.route('del', dst='default')
                    ipr.route('add', dst='default', gateway=ip_address)
        except Exception as e:
            return False, f"error {str(e)}"

        # Check if the command executed successfully
        
        return True, "Primary interface changed"
    def restart_service(self):
        try:
            subprocess.run(["sudo", "systemctl", "restart", "configuration-app.service"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except Exception:
            pass
    
    

    def check_ssh_status(self):
        try:
            # Run systemctl command to check SSH service status
            result = subprocess.run(['systemctl', 'is-active', 'ssh'], capture_output=True, text=True, check=True)
            status = result.stdout.strip()  # Get the status output
            
            if status == 'active':
                return True
                
            else:
                return False
        except subprocess.CalledProcessError:
            return False


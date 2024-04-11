import curses
import keyboard

from utils import shutdown_computer, get_ip_address, restart_computer
from constant import SYSTEM_CONFIG_LABEL, PASSWORD_LABEL, USERNAME_LABEL, NOVAIGU_HTTP_LABEL, \
    NOVAIGU_PLATFORM_LABEL, NOVAIGU_LABEL, F2_CONFIGURATION_SYSTEM, SHUT_DOWN_RESTART, AUTHENTICATION_SCREEN, KEY_ESC, \
    ESC_CANCLE, F11_RESTART, F2_SHUT_DOWN, PASSWORD, HOSTNAME, SSH, LOCK_DOWN_MODE,KEY_DOWN,KEY_UP,MANAGEMENT_INTERFACE, NETWORK_ADAPTOR, IP_CONFIGURATION, DNS_SERVER
from dialogs.restart_shutdown import ShutdownRestart
from dialogs.authentication import AuthenticationScreen
from dialogs.update_password import UpdatePasswordScreen
from dialogs.hostname import HostnameScreen
from dialogs.system_config import SystemConfig
from dialogs.lock_down_mode import LockdownModeScreen
from dialogs.ssh import SSHScreen
from dialogs.configure_management import ConfigureManagement
from dialogs.ip_configuration import IPConfigurationScreen
from dialogs.net_work_adaptor import NetworkAdaptorScreen
from dialogs.dns_configuration import DNSScreen
from logs.udr_logger import UdrLogger
from  system_controller.systemcontroler import SystemControler


class NovaiguApplication:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_selected = USERNAME_LABEL
        self.username_input = ""
        self.password_input = ""
        self.logger_ = UdrLogger()
        self.popup_window = ShutdownRestart(stdscr.getmaxyx()[0], stdscr.getmaxyx()[1], self)
        self.update_password = UpdatePasswordScreen(stdscr.getmaxyx()[0], stdscr.getmaxyx()[1], self)
        self.host_name = HostnameScreen(stdscr.getmaxyx()[0], stdscr.getmaxyx()[1], self)
        self.system_controller  = SystemControler()
        self.setup_windows()

    def setup_windows(self):
        # Initialize curses
        keyboard.on_press(self._on_key_press)
        curses.start_color()
        curses.use_default_colors()

        # Set up color pairs
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Grey background
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)  # Orange background
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        

        # Get screen dimensions
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()

        # Calculate dimensions for the two partitions
        top_height = int(0.6 * self.screen_height)
        bottom_height = self.screen_height - top_height

        # Create windows for each partition
        self.top_win = curses.newwin(top_height, self.screen_width, 0, 0)
        self.bottom_win = curses.newwin(bottom_height, self.screen_width, top_height, 0)

        # Set background colors for each partition
        self.top_win.bkgd(' ', curses.color_pair(1))  # Grey background
        self.bottom_win.bkgd(' ', curses.color_pair(2))  # Orange background

        # Draw borders to distinguish the partitions
        self.stdscr.hline(top_height, 0, '-', self.screen_width)
        self.stdscr.refresh()

        # Refresh the windows to apply changes
        self.top_win.refresh()
        self.bottom_win.refresh()

        ip_address = self.system_controller.get_ip_address()
        novaigu_http_address = NOVAIGU_HTTP_LABEL.format(ip_address)

        # Calculate positions for labels
        label_width = max(len(NOVAIGU_LABEL), len(NOVAIGU_PLATFORM_LABEL), len(novaigu_http_address))
        label_height = 2
        label_x = (self.screen_width - label_width) // 2
        label_y = top_height // 2

        # Add labels to self.top_win
        self.top_win.addstr(label_y, label_x, NOVAIGU_LABEL)
        self.top_win.addstr(label_y + label_height, label_x, NOVAIGU_PLATFORM_LABEL)
        self.top_win.addstr(label_y + 2 * label_height, label_x, novaigu_http_address)

        # Refresh the self.top_win to apply changes
        self.top_win.refresh()

        # Add clickable label at the bottom-left corner
        self.bottom_win.addstr(bottom_height - 2, 2, F2_CONFIGURATION_SYSTEM, curses.A_UNDERLINE)
        self.bottom_win.addstr(bottom_height - 2, self.screen_width - len("<F12> Shut down/Restart") - 2,
                                "<F12> Shut down/Restart", curses.A_UNDERLINE)
        self.bottom_win.refresh()

    def create_shut_down_restart_pop_up(self):
        self.set_main_screen_black()
        self.popup_window.create_shut_down_restart_pop_up(self.stdscr)
     
    def get_current_screen(self):
        
        if hasattr(self, 'system_config') and self.system_config != None:
            current_index= self.system_config.selected_index
            current_field = self.system_config.labels[current_index]
            return current_field

    def _on_key_press(self, event):
        
        current_screen = self.get_current_screen()       
        if event.name == KEY_DOWN  :
            
            if   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                self.configuration_management_screen.handle_arrow_key(event.name)
            
            elif  hasattr(self, 'system_config') and self.system_config != None and self.system_config.active_status ==True :
                self.system_config.handle_arrow_key(event.name)
            
            
        

        elif event.name == KEY_UP:
            if   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                self.configuration_management_screen.handle_arrow_key(event.name)
            
            elif hasattr(self, 'system_config') and self.system_config != None and  self.system_config.active_status ==True :
                self.system_config.handle_arrow_key(event.name)

        
        elif event.name == KEY_ESC:
            self.logger_.log_info("125 {}".format(event.name))   
            if self.popup_window.popup_win:
                self.popup_window.popup_win.clear()  # KEY_ESC the pop-up window
                self.popup_window.popup_win.refresh()
                self.popup_window.popup_win.deleteln()
                self.popup_window.popup_win = None
                self.reset_main_screen_color()
            

            elif current_screen == PASSWORD and hasattr(self, 'update_password')  and self.update_password !=None and self.update_password.update_status == True :
                self.system_config.active_status = True
                self.system_config.update_password_screen = False 
                self.update_password.clear()
                self.reset_system_config_screen()
                self.update_password = None

            elif current_screen == HOSTNAME and self.host_name.update_status == True :
                self.system_config.active_status = True
                self.system_config.update_password_screen = False 
                self.host_name.clear()
                self.reset_system_config_screen()
                self.host_name = None

            
            elif current_screen == SSH and self.ssh_screen.update_status == True :
                self.system_config.active_status = True
                self.system_config.update_password_screen = False 
                self.ssh_screen.clear()
                self.reset_system_config_screen()
                self.ssh_screen = None
            
            elif current_screen == LOCK_DOWN_MODE and self.lock_down_screen.update_status == True :
                self.system_config.active_status = True
                self.system_config.update_password_screen = False 
                self.lock_down_screen.clear()
                self.reset_system_config_screen()
                self.lock_down_screen = None
            
           
            
            elif current_screen == MANAGEMENT_INTERFACE and self.configuration_management_screen.update_status == True :
                self.logger_.log_info("164 {}".format(event.name)) 
                self.system_config.active_status = True
                self.system_config.update_password_screen = False 
                
                selected_index = self.configuration_management_screen.selected_index
                selected_label = self.configuration_management_screen.labels[selected_index]
                if selected_label ==  IP_CONFIGURATION and  hasattr(self, 'ip_config_adaptor')  and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True:
                    
                    self.ip_config_adaptor.clear()
                    self.ip_config_adaptor = None
                    self.configuration_management_screen.reset_screen_color()
                    self.configuration_management_screen.handle_arrow_key("up")

                elif selected_label ==  NETWORK_ADAPTOR and  hasattr(self, 'net_work_screen')  and self.net_work_screen !=None and self.net_work_screen.update_status == True:
                    
                    self.net_work_screen.clear()
                    self.net_work_screen = None
                    self.configuration_management_screen.reset_screen_color()
                    self.configuration_management_screen.handle_arrow_key("up")
                
                elif selected_label ==  DNS_SERVER and  hasattr(self, 'dns_screen')  and self.dns_screen !=None and self.dns_screen.update_status == True:
                    self.dns_screen.clear()
                    self.dns_screen = None
                    self.configuration_management_screen.reset_screen_color()
                    self.configuration_management_screen.handle_arrow_key("up")
            
                else:
                    
                    self.configuration_management_screen.clear()
                    self.reset_system_config_screen()
                    self.configuration_management_screen = None
            

            elif hasattr(self, 'system_config')  and self.system_config !=None and  self.system_config.active_status == True:
                self.logger_.log_info("172 {}".format(event.name))     
                self.system_config.active_status =False
                self.system_config.system_configuration_screen.clear()
                self.system_config.system_configuration_screen = None
                self.system_config = None
                self.reset_main_screen_color()

            
                    
            
            elif self.authentication_screen.authentication_screen:  
                self.logger_.log_info("else {}".format(event.name))               
                self.current_selected = USERNAME_LABEL
                # self.clear_authetication_screen()
                self.reset_main_screen_color()
            
            


        elif event.name == "f2":
            if self.popup_window.popup_win:
                self.system_controller.shutdown_system()
                # shutdown_computer()
            else:
                self.username_input = ""
                self.password_input = ""
                self.set_main_screen_black()
                self.authentication_screen = AuthenticationScreen(self.stdscr, self.screen_height, self.screen_width)
        elif event.name == "f11":
            if self.popup_window.popup_win:
                self.system_controller.restart_computer()
                # restart_computer()
        elif event.name == "f12":
            self.create_shut_down_restart_pop_up()

        elif event.name == "enter":
            if hasattr(self, 'authentication_screen'):
                if (len(self.authentication_screen.username_input) > 0 or len(self.authentication_screen.password_input) > 0 )  and not hasattr(self, 'system_config'):
                    response = self.system_controller.authenticate(self.authentication_screen.username_input,self.authentication_screen.password_input)
                    if response:
                        self.username_input = self.authentication_screen.username_input
                        self.password_input = self.authentication_screen.password_input
                        self.authentication_screen. clear_input_field()
                        self.system_config = SystemConfig(self.stdscr.getmaxyx()[0], self.stdscr.getmaxyx()[1], self)
                        self.system_config.create_system_configuration()
                        self.system_config.update_password_screen = True 
                
                elif  (len(self.authentication_screen.username_input) > 0 or len(self.authentication_screen.password_input) > 0 )  and  hasattr(self, 'system_config') and self.system_config == None:
                    self.authentication_screen. clear_input_field()
                    self.system_config = SystemConfig(self.stdscr.getmaxyx()[0], self.stdscr.getmaxyx()[1], self)
                    self.system_config.create_system_configuration()
                    self.system_config.update_password_screen = True 
                    
                
                elif current_screen == PASSWORD:
                    if  hasattr(self, 'update_password')  and self.update_password !=None  and self.update_password.update_status == True  :
                        self.logger_.log_info("self.self.update_password.current_password {} == self.password_input {}".format(self.update_password.current_password,self.password_input))
                        if self.update_password.current_password == self.password_input: 
                            self.logger_.log_info("self.username_input {} == self.password_input{}".format(self.username_input,self.password_input,self.update_password.new_password))
                            status = self.system_controller.change_password(self.username_input,self.password_input,self.update_password.new_password)
                            if status:
                                self.system_config.active_status = True
                                self.system_config.update_password_screen = False 
                                self.update_password.clear()
                                self.reset_system_config_screen()
                                self.update_password = None
                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.update_password = UpdatePasswordScreen(self.screen_height, self.screen_width,self)
                        self.update_password.update_status = True
                elif current_screen == HOSTNAME:
                    if   hasattr(self, 'host_name')  and self.host_name !=None  and self.host_name.update_status == True  :
                        self.system_config.active_status = True
                        self.system_config.update_password_screen = False 
                        self.host_name.clear()
                        self.reset_system_config_screen()
                        self.host_name = None
                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.host_name = HostnameScreen(self.screen_height, self.screen_width,self)
                        self.host_name.update_status = True    
                elif current_screen == SSH:
                     
                    if   hasattr(self, 'ssh_screen')  and self.ssh_screen !=None  and self.ssh_screen.update_status == True  :
                        self.system_config.active_status = True
                        self.system_config.update_password_screen = False 
                        self.ssh_screen.clear()
                        self.reset_system_config_screen()
                        self.ssh_screen = None
                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.ssh_screen = SSHScreen(self.screen_height, self.screen_width,self)
                        self.ssh_screen.update_status = True 
                elif current_screen == LOCK_DOWN_MODE:
                    if   hasattr(self, 'lock_down_screen')  and self.lock_down_screen !=None  and self.lock_down_screen.update_status == True  :
                        self.system_config.active_status = True
                        self.system_config.update_password_screen = False 
                        self.lock_down_screen.clear()
                        self.reset_system_config_screen()
                        self.lock_down_screen = None
                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.lock_down_screen = LockdownModeScreen(self.screen_height, self.screen_width,self)
                        self.lock_down_screen.update_status = True  
                
                elif current_screen == MANAGEMENT_INTERFACE:
                    if   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                        selected_index = self.configuration_management_screen.selected_index
                        selected_label = self.configuration_management_screen.labels[selected_index]
                        if selected_label ==  IP_CONFIGURATION:
                            if hasattr(self, 'ip_config_adaptor')  and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True:
                                self.ip_config_adaptor.clear()
                                self.ip_config_adaptor = None
                                self.configuration_management_screen.reset_screen_color()
                                self.configuration_management_screen.handle_arrow_key("up")                                
                                # self.configuration_management_screen.reset_screen_color()

                            else:      
                                self.configuration_management_screen.set_sytem_config_screen_dark()
                                self.ip_config_adaptor = IPConfigurationScreen(self.screen_height, self.screen_width,self)
                                self.ip_config_adaptor.update_status =True
                                self.configuration_management_screen.update_status = True


                        elif  selected_label ==  NETWORK_ADAPTOR:
                            if hasattr(self, 'net_work_screen')  and self.net_work_screen !=None and self.net_work_screen.update_status == True:
                                self.net_work_screen.clear()
                                self.net_work_screen = None
                                self.configuration_management_screen.reset_screen_color()
                                self.configuration_management_screen.handle_arrow_key("up")                                
                                
                            else:      
                                self.configuration_management_screen.set_sytem_config_screen_dark()
                                self.net_work_screen = NetworkAdaptorScreen(self.screen_height, self.screen_width,self)
                                self.net_work_screen.update_status =True
                                self.configuration_management_screen.update_status = True

                        elif  selected_label ==  DNS_SERVER:
                            if hasattr(self, 'dns_screen')  and self.dns_screen !=None and self.dns_screen.update_status == True:
                                self.dns_screen.clear()
                                self.dns_screen = None
                                self.configuration_management_screen.reset_screen_color()
                                self.configuration_management_screen.handle_arrow_key("up")                                
                                
                            else:      
                                self.configuration_management_screen.set_sytem_config_screen_dark()
                                self.dns_screen = DNSScreen(self.screen_height, self.screen_width,self)
                                self.dns_screen.update_status =True
                                self.configuration_management_screen.update_status = True

                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.configuration_management_screen = ConfigureManagement(self.screen_height, self.screen_width,self)
                        self.configuration_management_screen.create_configuration_management()
                        self.configuration_management_screen.update_status = True  
                else:
                  
                    current_sys_config = self.get_current_screen()
                    if current_sys_config == HOSTNAME:
                        self.host_name = HostnameScreen(stdscr.getmaxyx()[0], stdscr.getmaxyx()[1], self)
            else:
                self.current_selected = USERNAME_LABEL
                self.set_main_screen_black()

        elif event.name == "tab" :
            if hasattr(self, 'update_password') and self.update_password !=None and current_screen == PASSWORD:
                self.update_password.handle_key_event(event)
            elif  hasattr(self, 'authentication_screen') and self.authentication_screen !=None and self.authentication_screen.current_status == "username":
                self.authentication_screen.current_status = "password"
            elif  hasattr(self, 'authentication_screen') and self.authentication_screen !=None and self.authentication_screen.current_status == "password":
                self.authentication_screen.current_status = "username"

        elif event.name == "backspace":
            if hasattr(self, 'update_password') and self.update_password !=None and  self.update_password.update_status == True and current_screen == PASSWORD:
                self.update_password.handle_key_event(event) 

            elif hasattr(self, 'host_name') and self.host_name !=None and self.host_name.update_status == True and current_screen == HOSTNAME:
                self.host_name.handle_key_event(event)            
            

            if self.current_selected == USERNAME_LABEL:
                self.username_input = self.authentication_screen.get_username_input()
            else:
                self.password_input = self.authentication_screen.get_password_input()
            
            if hasattr(self, 'authentication_screen') and self.authentication_screen !=None:
                self.authentication_screen.handle_key_event(event)

        elif event.name == "space":
            if hasattr(self, 'ssh_screen') and self.ssh_screen !=None and self.ssh_screen.update_status == True and current_screen == SSH:  
                self.logger_.log_info("272 ssh screen {}".format(event.name))
                self.ssh_screen.handle_arrow_key(event)
                
            elif hasattr(self, 'lock_down_screen') and self.lock_down_screen !=None and self.lock_down_screen.update_status == True and current_screen == LOCK_DOWN_MODE:  
                self.logger_.log_info("276 ssh screen {}".format(event.name))
                self.lock_down_screen.handle_arrow_key(event)
            
            elif   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                selected_index = self.configuration_management_screen.selected_index
                selected_label = self.configuration_management_screen.labels[selected_index]
                if hasattr(self, 'ip_config_adaptor') and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True and selected_label == IP_CONFIGURATION:  
                    self.logger_.log_info("349 ssh screen {}".format(event.name))
                    self.ip_config_adaptor.handle_arrow_key(event)
                elif hasattr(self, 'net_work_screen') and self.net_work_screen !=None and self.net_work_screen.update_status == True and selected_label == NETWORK_ADAPTOR:  
                    self.logger_.log_info("349 ssh screen {}".format(event.name))
                    self.net_work_screen.handle_arrow_key(event) 
                elif hasattr(self, 'dns_screen') and self.dns_screen !=None and self.dns_screen.update_status == True and selected_label == DNS_SERVER:  
                    self.logger_.log_info("349 ssh screen {}".format(event.name))
                    self.dns_screen.handle_arrow_key(event)

                    
        else:
            if hasattr(self, 'update_password') and self.update_password !=None and  self.update_password.update_status == True and current_screen == PASSWORD:
                self.update_password.handle_key_event(event)
            elif hasattr(self, 'host_name') and self.host_name !=None and self.host_name.update_status == True and current_screen == HOSTNAME:
                self.host_name.handle_key_event(event)
            elif hasattr(self, 'authentication_screen') and self.authentication_screen !=None:
                self.authentication_screen.handle_key_event(event)
            else:
                pass 
                

    def set_sytem_config_screen_dark(self):
        self.system_config.sc_config_top_win.bkgd(' ', curses.color_pair(0))  # Yellow background
        self.system_config.sc_config_bottom_win.bkgd(' ', curses.color_pair(0))  # Grey background
        self.system_config.sc_config_top_win.refresh()
        self.system_config.sc_config_bottom_win.refresh()
    
    def reset_system_config_screen(self):
        self.system_config.sc_config_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        self.system_config.sc_config_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background
        self.system_config.sc_config_top_win.refresh()
        self.system_config.sc_config_bottom_win.refresh()
        self.system_config.handle_arrow_key("up")

    def clear_system_configuration_screen(self):
        self.system_config.system_configuration_screen.clear()
        self.system_config.system_configuration_screen = None
    
    def set_main_screen_black(self):
        self.top_win.bkgd(' ', curses.color_pair(0))  # Black background
        self.bottom_win.bkgd(' ', curses.color_pair(0))
        self.top_win.refresh()
        self.bottom_win.refresh()

    def reset_main_screen_color(self):
        self.top_win.bkgd(' ', curses.color_pair(1))  # Grey background
        self.bottom_win.bkgd(' ', curses.color_pair(2))  # Orange background
        self.top_win.refresh()
        self.bottom_win.refresh()

    def create_system_configuration(self):
        self.set_main_screen_black()

        sc_config_height, sc_config_width = int(self.screen_height * 0.98), int(self.screen_width * 0.99)
        sc_config_x = int(self.screen_width * 0.015)
        sc_config_y = int(self.screen_height * 0.025)

        self.system_configuration_screen = curses.newwin(sc_config_height, sc_config_width, sc_config_y, sc_config_x)

        # Calculate dimensions for the two partitions within the pop-up window
        sc_config_top_height = max(int(0.6 * sc_config_height), 1)
        sc_config_bottom_height = sc_config_height - sc_config_top_height

        # Create windows for each partition within the pop-up window
        sc_config_top_win = self.system_configuration_screen.subwin(sc_config_top_height, sc_config_width, sc_config_y,
                                                                     sc_config_x)
        sc_config_bottom_win = self.system_configuration_screen.subwin(sc_config_bottom_height, sc_config_width,
                                                                        sc_config_y + sc_config_top_height, sc_config_x)

        # Set background colors for each partition within the pop-up window
        sc_config_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        sc_config_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background

        # system configuration label
        sc_config_top_win.addstr(1, 2, SYSTEM_CONFIG_LABEL, curses.color_pair(4))
        sc_config_top_win.addstr(3, 2, PASSWORD, curses.color_pair(4))
        sc_config_top_win.addstr(4, 2, HOSTNAME, curses.color_pair(4))
        sc_config_top_win.addstr(5, 2, SSH, curses.color_pair(4))
        sc_config_top_win.addstr(6, 2, LOCK_DOWN_MODE, curses.color_pair(4))

        self.system_configuration_screen.refresh()

    def run(self):
        while True:
            pass


def main(stdscr):
    app = NovaiguApplication(stdscr)
    app.run()


curses.wrapper(main)

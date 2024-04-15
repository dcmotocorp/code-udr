import curses
import keyboard
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

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
from data.database import UserDatabase

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
        self.user_data_base = UserDatabase()
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
        curses.curs_set(0)

    def create_shut_down_restart_pop_up(self):
        self.logger_.log_info("Shut down and restart pop up")
        self.set_main_screen_black()
        self.popup_window.create_shut_down_restart_pop_up(self.stdscr)
     
    def get_current_screen(self):
        
        if hasattr(self, 'system_config') and self.system_config != None:
            current_index= self.system_config.selected_index
            current_field = self.system_config.labels[current_index]
            return current_field

    def clear_authetication_screen(self):
        self.authentication_screen.clear_input_field()
        self.authentication_screen.clear()
        self.authentication_screen = None

    def _on_key_press(self, event):
        
        current_screen = self.get_current_screen()       
        if event.name == KEY_DOWN  :
            try: 
                
                if   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                    
                    if hasattr(self, 'net_work_screen')  and self.net_work_screen !=None and self.net_work_screen.update_status == True:
                        self.net_work_screen.handle_arrow_key(event)
                    elif hasattr(self, 'ip_config_adaptor')  and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True:
                        self.ip_config_adaptor.handle_arrow_key(event)
                    elif hasattr(self, 'dns_screen')  and self.dns_screen !=None and self.dns_screen.update_status == True:
                        self.dns_screen.handle_arrow_key(event)
                    else:
                        self.configuration_management_screen.handle_arrow_key(event.name)
                
                elif hasattr(self, 'update_password') and self.update_password != None and  self.update_password.update_status ==True :
                    self.update_password.handle_arrow_key(event)
                
                elif hasattr(self, 'host_name') and self.host_name != None and  self.host_name.update_status ==True :
                    self.host_name.handle_arrow_key(event)
                
                elif hasattr(self, 'ssh_screen') and self.ssh_screen != None and  self.ssh_screen.update_status ==True :
                    self.ssh_screen.handle_arrow_key(event.name)
                
                elif hasattr(self, 'lock_down_screen') and self.lock_down_screen != None and  self.lock_down_screen.update_status ==True :
                    self.lock_down_screen.handle_arrow_key(event.name)
                
                elif  hasattr(self, 'system_config') and self.system_config != None and self.system_config.active_status ==True :
                    self.system_config.handle_arrow_key(event.name)
            
            except Exception as ex:
                self.logger_.log_info("Exception while key down {}".format(str(ex)))
        

        elif event.name == KEY_UP:
            try:
                if   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                    if hasattr(self, 'net_work_screen')  and self.net_work_screen !=None and self.net_work_screen.update_status == True:
                        self.net_work_screen.handle_arrow_key(event)
                    elif hasattr(self, 'ip_config_adaptor')  and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True:
                        self.ip_config_adaptor.handle_arrow_key(event)
                    elif hasattr(self, 'dns_screen')  and self.dns_screen !=None and self.dns_screen.update_status == True:
                        self.dns_screen.handle_arrow_key(event)
                    else:
                        self.configuration_management_screen.handle_arrow_key(event.name)
                
                elif hasattr(self, 'host_name') and self.host_name != None and  self.host_name.update_status ==True :
                    self.host_name.handle_arrow_key(event)

                elif hasattr(self, 'ssh_screen') and self.ssh_screen != None and  self.ssh_screen.update_status ==True :
                    self.ssh_screen.handle_arrow_key(event.name)

                elif hasattr(self, 'update_password') and self.update_password != None and  self.update_password.update_status ==True :
                    self.update_password.handle_arrow_key(event)

                elif hasattr(self, 'lock_down_screen') and self.lock_down_screen != None and  self.lock_down_screen.update_status ==True :
                    self.lock_down_screen.handle_arrow_key(event.name)
                
                elif hasattr(self, 'system_config') and self.system_config != None and  self.system_config.active_status ==True :
                    self.system_config.handle_arrow_key(event.name)
            
            except Exception as ex:
                self.logger_.log_info("Exception while key up {}".format(str(ex)))

            

        
        elif event.name == KEY_ESC:
            try:  
                if self.popup_window.popup_win:
                    self.popup_window.popup_win.clear()  # KEY_ESC the pop-up window
                    self.popup_window.popup_win.refresh()
                    self.popup_window.popup_win.deleteln()
                    self.popup_window.popup_win = None
                    self.reset_main_screen_color()
                    self.logger_.log_info("Clear pop up window")
                

                elif current_screen == PASSWORD and hasattr(self, 'update_password')  and self.update_password !=None and self.update_password.update_status == True :
                    self.system_config.active_status = True
                    self.system_config.update_password_screen = False 
                    self.update_password.clear()
                    self.reset_system_config_screen()
                    self.update_password = None
                    self.logger_.log_info("Clear pop up password screen")

                elif current_screen == HOSTNAME and hasattr(self, 'host_name')  and self.host_name !=None and self.host_name.update_status == True :
                    self.system_config.active_status = True
                    self.system_config.update_password_screen = False 
                    self.host_name.clear()
                    self.reset_system_config_screen()
                    self.host_name = None
                    self.logger_.log_info("Clear pop up hostname screen")

                
                elif current_screen == SSH and hasattr(self, 'ssh_screen')  and self.ssh_screen !=None and self.ssh_screen.update_status == True :
                    self.system_config.active_status = True
                    self.system_config.update_password_screen = False 
                    self.ssh_screen.clear()
                    self.reset_system_config_screen()
                    self.ssh_screen = None
                    self.logger_.log_info("Clear pop up ssh screen")
                
                elif current_screen == LOCK_DOWN_MODE and hasattr(self, 'lock_down_screen')  and self.lock_down_screen !=None and self.lock_down_screen.update_status == True :
                    self.system_config.active_status = True
                    self.system_config.update_password_screen = False 
                    self.lock_down_screen.clear()
                    self.reset_system_config_screen()
                    self.lock_down_screen = None
                    self.logger_.log_info("Clear pop up lock down screen")
                
            
                
                elif current_screen == MANAGEMENT_INTERFACE and hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None and self.configuration_management_screen.update_status == True :
                    try:                    
                        self.system_config.active_status = True
                        self.system_config.update_password_screen = False 
                        
                        selected_index = self.configuration_management_screen.selected_index
                        selected_label = self.configuration_management_screen.labels[selected_index]
                        if selected_label ==  IP_CONFIGURATION and  hasattr(self, 'ip_config_adaptor')  and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True:
                            
                            if self.ip_config_adaptor.current_selected_label_index ==1 :
                                self.ip_config_adaptor.set_manually_ip() 
                            elif self.ip_config_adaptor.current_selected_label_index ==0:
                                self.ip_config_adaptor.set_ip_address_automatic()
                            else:
                                pass 
                            self.ip_config_adaptor.clear()
                            self.ip_config_adaptor = None
                            self.configuration_management_screen.reset_screen_color()
                            self.configuration_management_screen.refresh_screen()

                        elif selected_label ==  NETWORK_ADAPTOR and  hasattr(self, 'net_work_screen')  and self.net_work_screen !=None and self.net_work_screen.update_status == True:
                            
                            self.net_work_screen.clear()
                            self.net_work_screen = None
                            self.configuration_management_screen.reset_screen_color()
                            self.configuration_management_screen.refresh_screen()
                        
                        elif selected_label ==  DNS_SERVER and  hasattr(self, 'dns_screen')  and self.dns_screen !=None and self.dns_screen.update_status == True:
                            
                            if self.dns_screen.current_selected_label_index ==1:
                                self.dns_screen.set_manually_dns()
                            elif self.dns_screen.current_selected_label_index==0:
                                self.dns_screen.set_auto_dns()
                            else:
                                pass 
                            self.dns_screen.clear()
                            self.dns_screen = None
                            self.configuration_management_screen.reset_screen_color()
                            self.configuration_management_screen.refresh_screen()
                    
                        else:
                            
                            self.configuration_management_screen.clear()
                            self.reset_system_config_screen()
                            self.configuration_management_screen = None
                    except Exception as ex:
                        self.logger_.log_info("Exception occure in management interface {}".format(str(ex)))

                elif hasattr(self, 'system_config')  and self.system_config !=None and  self.system_config.active_status == True:
                    try:
                        self.logger_.log_info("172 {}".format(event.name))     
                        self.system_config.active_status =False
                        self.system_config.system_configuration_screen.clear()
                        self.system_config.system_configuration_screen = None
                        self.system_config = None
                        self.clear_authetication_screen()
                        self.reset_main_screen_color()
                    except Exception as ex:
                        self.logger_.log_info("Exception occure in system config on pressing esc")
                
                        
                
                elif hasattr(self, 'authentication_screen')  and self.authentication_screen !=None and self.authentication_screen.authentication_screen:  
                    try:               
                    
                        self.current_selected = USERNAME_LABEL
                        self.clear_authetication_screen()
                        self.reset_main_screen_color()
                    except Exception as ex:
                        self.logger_.log_info("Exception occure in authetication ssystem on pressing esc") 
                else:
                    pass 
                
            except Exception as ex:
                self.logger_.log_info("Exception while pressing key ESC {}".format(str(ex)))


        elif event.name == "f2":
            if self.popup_window.popup_win:
                self.logger_.log_info("shut down system  press f2")
                self.system_controller.shutdown_system()

            else:
                self.username_input = ""
                self.password_input = ""
                self.set_main_screen_black()
                self.logger_.log_info("open Authentication system")
                self.user_data_base._init_database()
                self.authentication_screen = AuthenticationScreen(self.stdscr, self.screen_height, self.screen_width)
                self.logger_.log_info("Current Authentication system")
        elif event.name == "f11":
            if self.popup_window.popup_win:
                self.system_controller.restart_computer()
    
        elif event.name == "f12":
            self.create_shut_down_restart_pop_up()

        elif event.name =="shift":
            if hasattr(self, 'authentication_screen') and self.authentication_screen !=None:
                self.authentication_screen.handle_key_event(event)

        
        elif event.name == "enter":
            if hasattr(self, 'authentication_screen') and self.authentication_screen != None  :
                if (len(self.authentication_screen.username_input) > 0 and len(self.authentication_screen.password_input) > 0 )  and not hasattr(self, 'system_config'):
                    self.logger_.log_info("Current username and password match the condition")
                    response = self.system_controller.authenticate(self.authentication_screen.username_input,self.authentication_screen.password_input)
                    self.logger_.log_info("authentication resposne {}".format(response))
                    if response:
                        try:
                            try :                                
                                check_username = self.user_data_base.get_user_details(self.authentication_screen.username_input)
                                if not check_username:
                                    self.user_data_base.add_user(self.authentication_screen.username_input, self.authentication_screen.password_input)
                                
                                self.user_data_base.update_current_login(self.authentication_screen.username_input)
                                

                                # self.user_data_base.update_current_login(self.authentication_screen.username_input)
                            except Exception as ex:
                                self.logger_.log_info("Exception error in database resposne {}".format(str(ex)))
                            self.username_input = self.authentication_screen.username_input
                            self.password_input = self.authentication_screen.password_input
                            self.authentication_screen. clear_input_field()
                            self.system_config = SystemConfig(self.stdscr.getmaxyx()[0], self.stdscr.getmaxyx()[1], self)
                            self.system_config.create_system_configuration()
                            self.system_config.update_password_screen = True 
                            self.logger_.log_info("switch to system config screen")
                        except Exception as ex:
                            self.logger_.log_info("Exception while switching to config screen {}".format(ex))
                            pass 
                elif  (len(self.authentication_screen.username_input) > 0 and len(self.authentication_screen.password_input) > 0 )  and  hasattr(self, 'system_config') and self.system_config == None:
                    try:
                        response = self.system_controller.authenticate(self.authentication_screen.username_input,self.authentication_screen.password_input)
                        self.logger_.log_info("authentication resposne {}".format(response))
                        if response:
                            try:
                                check_username = self.user_data_base.get_user_details(self.authentication_screen.username_input)
                                if not check_username:
                                    self.user_data_base.add_user(self.authentication_screen.username_input, self.authentication_screen.password_input)
                                self.user_data_base.update_current_login(self.authentication_screen.username_input)
                                # self.user_data_base.update_current_login(self.authentication_screen.username_input)
                            except Exception as ex:
                                self.logger_.log_info("Exception error in database resposne {}".format(str(ex)))
                            self.authentication_screen.clear_input_field()
                            self.system_config = SystemConfig(self.stdscr.getmaxyx()[0], self.stdscr.getmaxyx()[1], self)
                            self.system_config.create_system_configuration()
                            self.system_config.update_password_screen = True 
                    except Exception as ex:
                        self.logger_.log_info("Exception while creating to config screen {}".format(ex))

                
                elif current_screen == PASSWORD:
                    if  hasattr(self, 'update_password')  and self.update_password !=None  and self.update_password.update_status == True  :
                        
                        current_user_name = self.user_data_base.get_current_login()
                        response = self.system_controller.authenticate(current_user_name,self.update_password.current_password)
                        if response:
                        # if self.update_password.current_password == self.password_input: 
                            self.logger_.log_info("self.username_input {} == self.password_input{}".format(self.username_input,self.password_input))
                            status = self.system_controller.change_password(self.username_input,self.password_input,self.update_password.new_password)
                            if status:
                                self.user_data_base.change_password(self.username_input,self.update_password.new_password)
                                self.system_config.active_status = True
                                self.system_config.update_password_screen = False 
                                self.update_password.clear()
                                self.reset_system_config_screen()
                                self.update_password = None
                                curses.curs_set(0)
                                
                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.update_password = UpdatePasswordScreen(self.screen_height, self.screen_width,self)
                        self.update_password.update_status = True
                elif current_screen == HOSTNAME:
                    if   hasattr(self, 'host_name')  and self.host_name !=None  and self.host_name.update_status == True  :
                        if len(self.host_name.current_hostname) >0:
                            self.system_controller.set_hostname(self.host_name.current_hostname)
                            self.system_config.active_status = True
                            self.system_config.update_password_screen = False 
                            self.host_name.clear()
                            self.reset_system_config_screen()
                            self.host_name = None
                            curses.curs_set(0)
                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.host_name = HostnameScreen(self.screen_height, self.screen_width,self)
                        self.host_name.update_status = True    
                elif current_screen == SSH:
                     
                    if   hasattr(self, 'ssh_screen')  and self.ssh_screen !=None  and self.ssh_screen.update_status == True  :
                        try:
                            selected_value = self.ssh_screen.current_label_head
                            self.logger_.log_info("ssh screen username {} selected_value {}".format(self.username_input,selected_value))

                            if selected_value == 0:    
                                self.logger_.log_info("inside 0 ssh screen username {} selected_value {}".format(self.username_input,selected_value))
                                self.user_data_base.update_user_settings(self.username_input,ssh_enable=True)
                                self.system_controller.enable_ssh()
                            elif selected_value == 1:
                                self.logger_.log_info("inside 1 ssh screen username {} selected_value {}".format(self.username_input,selected_value))
                                self.user_data_base.update_user_settings(self.username_input,ssh_enable=False)
                                self.system_controller.disable_ssh() 

                            self.system_config.active_status = True
                            self.system_config.update_password_screen = False 
                            self.ssh_screen.clear()
                            self.reset_system_config_screen()
                            self.ssh_screen = None
                        except Exception as ex:
                            self.logger_.log_info("Exception occure while cleaning ssh screen  {}".format(str(ex)))
                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.ssh_screen = SSHScreen(self.screen_height, self.screen_width,self)
                        self.ssh_screen.update_status = True 
                
                
                elif current_screen == LOCK_DOWN_MODE:
                    if   hasattr(self, 'lock_down_screen')  and self.lock_down_screen !=None  and self.lock_down_screen.update_status == True  :
                        selected_value = self.lock_down_screen.current_label_head
                        
                        if selected_value == 0:
                            self.logger_.log_info("lock down screen username {}".format(self.username_input))
                            self.user_data_base.update_user_settings(self.username_input,is_lockdown=True)
                            self.system_controller.enable_lockdown_mode()
                        elif selected_value == 1:
                            self.logger_.log_info("lock down screen username else {}".format(self.username_input))
                            self.user_data_base.update_user_settings(self.username_input,is_lockdown=False)
                            self.system_controller.exit_lockdown_mode()
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
                                if self.ip_config_adaptor.current_seleected_parameter ==0:
                                    self.user_data_base.update_user_settings(self.username_input,ip_manual=False) 
                                elif self.ip_config_adaptor.current_seleected_parameter ==1:
                                    self.user_data_base.update_user_settings(self.username_input,ip_manual=True)
                                self.ip_config_adaptor.clear()
                                self.ip_config_adaptor = None
                                self.configuration_management_screen.reset_screen_color()
                                self.configuration_management_screen.refresh_screen()

                            else:      
                                self.configuration_management_screen.set_sytem_config_screen_dark()
                                self.ip_config_adaptor = IPConfigurationScreen(self.screen_height, self.screen_width,self)
                                self.ip_config_adaptor.update_status =True
                                self.configuration_management_screen.update_status = True


                        elif  selected_label ==  NETWORK_ADAPTOR:
                            if hasattr(self, 'net_work_screen')  and self.net_work_screen !=None and self.net_work_screen.update_status == True:
                                self.net_work_screen.set_network_data()
                                self.net_work_screen.clear()
                                self.net_work_screen = None
                                self.configuration_management_screen.reset_screen_color()
                                self.configuration_management_screen.refresh_screen()                                
                                
                                
                            else:      
                                self.configuration_management_screen.set_sytem_config_screen_dark()
                                self.net_work_screen = NetworkAdaptorScreen(self.screen_height, self.screen_width,self)
                                self.net_work_screen.update_status =True
                                self.configuration_management_screen.update_status = True

                        elif  selected_label ==  DNS_SERVER:
                            if hasattr(self, 'dns_screen')  and self.dns_screen !=None and self.dns_screen.update_status == True:
                                if self.dns_screen.current_selected_label_index ==0:
                                    self.user_data_base.update_user_settings(self.username_input,dns_manual=False)
                                elif self.dns_screen.current_selected_label_index ==1:
                                    self.user_data_base.update_user_settings(self.username_input,dns_manual=True)                                
                                self.dns_screen.clear()
                                self.dns_screen = None
                                self.configuration_management_screen.reset_screen_color()
                                self.configuration_management_screen.refresh_screen()                                
                                
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
                # self.set_main_screen_black()

        elif event.name == "tab" :
            if hasattr(self, 'update_password') and self.update_password !=None and current_screen == PASSWORD:
                self.update_password.handle_key_event(event)
            elif   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                selected_index = self.configuration_management_screen.selected_index
                selected_label = self.configuration_management_screen.labels[selected_index]
                if hasattr(self, 'ip_config_adaptor') and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True and selected_label == IP_CONFIGURATION:  
                    self.ip_config_adaptor.handle_arrow_key(event)  
                elif hasattr(self, 'dns_screen') and self.dns_screen !=None and self.dns_screen.update_status == True and selected_label == DNS_SERVER:  
                    self.logger_.log_info("logg in configuration in  tab space config")
                    self.dns_screen.handle_arrow_key(event)
            elif  hasattr(self, 'authentication_screen') and self.authentication_screen !=None :
                self.authentication_screen.handle_key_event(event)


        elif event.name == "backspace":
            if hasattr(self, 'update_password') and self.update_password !=None and  self.update_password.update_status == True and current_screen == PASSWORD:
                self.update_password.handle_key_event(event) 

            elif hasattr(self, 'host_name') and self.host_name !=None and self.host_name.update_status == True and current_screen == HOSTNAME:
                self.host_name.handle_key_event(event)            
            
            elif   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                selected_index = self.configuration_management_screen.selected_index
                selected_label = self.configuration_management_screen.labels[selected_index]
                if hasattr(self, 'ip_config_adaptor') and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True and selected_label == IP_CONFIGURATION:  
                    self.ip_config_adaptor.handle_arrow_key(event)

                elif hasattr(self, 'dns_screen') and self.dns_screen !=None and self.dns_screen.update_status == True and selected_label == DNS_SERVER:  
                    self.logger_.log_info("logg in configuration in  back space config")
                    self.dns_screen.handle_arrow_key(event)

            if self.current_selected == USERNAME_LABEL:
                self.username_input = self.authentication_screen.get_username_input()
            else:
                self.password_input = self.authentication_screen.get_password_input()
            
            if hasattr(self, 'authentication_screen') and self.authentication_screen !=None:
                self.authentication_screen.handle_key_event(event)

        elif event.name == "space":
            if hasattr(self, 'ssh_screen') and self.ssh_screen !=None and self.ssh_screen.update_status == True and current_screen == SSH:  
                self.ssh_screen.handle_arrow_key(event)
                
            elif hasattr(self, 'lock_down_screen') and self.lock_down_screen !=None and self.lock_down_screen.update_status == True and current_screen == LOCK_DOWN_MODE:  
                self.lock_down_screen.handle_arrow_key(event)
            
            elif   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                selected_index = self.configuration_management_screen.selected_index
                selected_label = self.configuration_management_screen.labels[selected_index]
                if hasattr(self, 'ip_config_adaptor') and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True and selected_label == IP_CONFIGURATION:  
                    self.ip_config_adaptor.handle_arrow_key(event)
                elif hasattr(self, 'net_work_screen') and self.net_work_screen !=None and self.net_work_screen.update_status == True and selected_label == NETWORK_ADAPTOR:  
                    self.net_work_screen.handle_arrow_key(event) 
                elif hasattr(self, 'dns_screen') and self.dns_screen !=None and self.dns_screen.update_status == True and selected_label == DNS_SERVER:  
                    self.dns_screen.handle_arrow_key(event)

                    
        else:
            if hasattr(self, 'update_password') and self.update_password !=None and  self.update_password.update_status == True and current_screen == PASSWORD:
                self.logger_.log_info("logg in 593 ")
                self.update_password.handle_key_event(event)
            elif hasattr(self, 'host_name') and self.host_name !=None and self.host_name.update_status == True and current_screen == HOSTNAME:
                self.logger_.log_info("logg in 596 ")
                self.host_name.handle_key_event(event)
            elif   hasattr(self, 'configuration_management_screen')  and self.configuration_management_screen !=None  and self.configuration_management_screen.update_status == True  :
                self.logger_.log_info("logg in configuration ")
                selected_index = self.configuration_management_screen.selected_index
                selected_label = self.configuration_management_screen.labels[selected_index]
                if hasattr(self, 'ip_config_adaptor') and self.ip_config_adaptor !=None and self.ip_config_adaptor.update_status == True and selected_label == IP_CONFIGURATION:  
                    self.logger_.log_info("logg in configuration in config")
                    self.ip_config_adaptor.handle_arrow_key(event)
                elif hasattr(self, 'dns_screen') and self.dns_screen !=None and self.dns_screen.update_status == True and selected_label == DNS_SERVER:  
                    self.logger_.log_info("logg in configuration in  dns config")
                    self.dns_screen.handle_arrow_key(event)
            
            elif hasattr(self, 'authentication_screen') and self.authentication_screen !=None:
                self.authentication_screen.handle_key_event(event)
            
            
            else:
                self.logger_.log_info("logg in else ")
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
        self.system_config.refreash_command()
        

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
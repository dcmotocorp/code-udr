import curses
import keyboard

from utils import shutdown_computer, get_ip_address, restart_computer
from constant import SYSTEM_CONFIG_LABEL, PASSWORD_LABEL, USERNAME_LABEL, NOVAIGU_HTTP_LABEL, \
    NOVAIGU_PLATFORM_LABEL, NOVAIGU_LABEL, F2_CONFIGURATION_SYSTEM, SHUT_DOWN_RESTART, AUTHENTICATION_SCREEN, KEY_ESC, \
    ESC_CANCLE, F11_RESTART, F2_SHUT_DOWN, PASSWORD, HOSTNAME, SSH, LOCK_DOWN_MODE,KEY_DOWN,KEY_UP
from dialogs.restart_shutdown import ShutdownRestart
from dialogs.authentication import AuthenticationScreen
from dialogs.update_password import UpdatePasswordScreen
from dialogs.hostname import HostnameScreen
from dialogs.system_config import SystemConfig
from logs.udr_logger import UdrLogger

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

        ip_address = get_ip_address()
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
            if  hasattr(self, 'system_config') and self.system_config != None and self.system_config.active_status ==True :
                self.system_config.handle_arrow_key(event.name)
        elif event.name == KEY_UP:
            if hasattr(self, 'system_config') and self.system_config != None and  self.system_config.active_status ==True :
                self.system_config.handle_arrow_key(event.name)

        
        elif event.name == KEY_ESC:
            
            if self.popup_window.popup_win:
                self.logger_.log_info("pop up win {}".format(current_screen)) 
                self.popup_window.popup_win.clear()  # KEY_ESC the pop-up window
                self.popup_window.popup_win.refresh()
                self.popup_window.popup_win.deleteln()
                self.popup_window.popup_win = None
                self.reset_main_screen_color()
            

            elif current_screen == PASSWORD and hasattr(self, 'update_password')  and self.update_password !=None and self.update_password.update_status == True :
                self.logger_.log_info("password up win {}".format(current_screen)) 
                # self.system_config.active_status = True
                # self.system_config.update_password_screen = False 
                # self.update_password.clear()
                # self.update_password = None
                # self.reset_system_config_screen()


                self.system_config.active_status = True
                self.system_config.update_password_screen = False 
                self.update_password.clear()
                self.reset_system_config_screen()
                self.update_password = None

                
                self.logger_.log_info("password  end up win {}".format(current_screen))

            elif current_screen == HOSTNAME and self.host_name.update_status == True :
                self.logger_.log_info("hostname up win {}".format(current_screen)) 
                self.logger_.log_info("host name {}".format(current_screen)) 
                self.system_config.active_status = True
                self.system_config.update_password_screen = False 
                self.host_name.clear()
                self.reset_system_config_screen()
                self.logger_.log_info("host name end host name")

            elif hasattr(self, 'system_config')  and self.system_config !=None and  self.system_config.active_status == True:
                self.logger_.log_info("active ststus up win {}".format(current_screen)) 
                self.system_config.active_status =False
                self.system_config.system_configuration_screen.clear()
                self.system_config.system_configuration_screen = None
                self.system_config = None
                self.reset_main_screen_color()

            elif self.authentication_screen.authentication_screen: 
                
                self.current_selected = USERNAME_LABEL
                # self.clear_authetication_screen()
                self.reset_main_screen_color()


        elif event.name == "f2":
            if self.popup_window.popup_win:
                shutdown_computer()
            else:
                self.username_input = ""
                self.password_input = ""
                self.set_main_screen_black()
                self.authentication_screen = AuthenticationScreen(self.stdscr, self.screen_height, self.screen_width)
        elif event.name == "f11":
            if self.popup_window.popup_win:
                restart_computer()
        elif event.name == "f12":
            self.create_shut_down_restart_pop_up()

        elif event.name == "enter":
            self.logger_.log_info("175 line  up win {}".format(current_screen)) 
            if hasattr(self, 'authentication_screen'):
                self.logger_.log_info("176 line  up winsdjhgjsdf lskj {} === {} ==={}".format(self.authentication_screen.username_input,self.authentication_screen.password_input,hasattr(self, 'system_config'))) 
                if (len(self.authentication_screen.username_input) > 0 or len(self.authentication_screen.password_input) > 0 )  and not hasattr(self, 'system_config'):
                    self.logger_.log_info("179 line  up winsdjhgjsdf lskj {} === {} ==={}".format(self.authentication_screen.username_input,self.authentication_screen.password_input,hasattr(self, 'system_config'))) 
                    self.system_config = SystemConfig(self.stdscr.getmaxyx()[0], self.stdscr.getmaxyx()[1], self)
                    self.system_config.create_system_configuration()
                    self.system_config.update_password_screen = True 
                
                elif  (len(self.authentication_screen.username_input) > 0 or len(self.authentication_screen.password_input) > 0 )  and  hasattr(self, 'system_config') and self.system_config == None:
                    self.logger_.log_info("179 line  up winsdjhgjsdf lskj {} === {} ==={}".format(self.authentication_screen.username_input,self.authentication_screen.password_input,hasattr(self, 'system_config'))) 
                    self.system_config = SystemConfig(self.stdscr.getmaxyx()[0], self.stdscr.getmaxyx()[1], self)
                    self.system_config.create_system_configuration()
                    self.system_config.update_password_screen = True 
                    
                
                elif current_screen == PASSWORD:
                    if  hasattr(self, 'update_password')  and self.update_password !=None  and self.update_password.update_status == True  :
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
                        self.host_name.update_status = True
                    else:
                        self.set_main_screen_black()
                        self.system_config.set_sytem_config_screen_dark()
                        self.host_name = HostnameScreen(self.screen_height, self.screen_width,self)
                        self.host_name.update_status = True        
                
                else:
                    self.logger_.log_info("210 else part line  up win {}".format(current_screen)) 
                    
                    
                    current_sys_config = self.get_current_screen()
                    if current_sys_config == HOSTNAME:
                        self.host_name = HostnameScreen(stdscr.getmaxyx()[0], stdscr.getmaxyx()[1], self)
            else:
                self.current_selected = USERNAME_LABEL
                self.set_main_screen_black()

        elif event.name == "tab" :
            if hasattr(self, 'update_password') and self.update_password !=None and current_screen == PASSWORD:
                self.update_password.handle_key_event(event)
            elif  self.authentication_screen.current_status == "username":
                self.authentication_screen.current_status = "password"
            elif self.authentication_screen.current_status == "password":
                self.authentication_screen.current_status = "username"

        elif event.name == "backspace":
            if self.update_password.update_status == True and current_screen == PASSWORD:
                self.update_password.handle_key_event(event)            
            
            if self.current_selected == USERNAME_LABEL:
                self.username_input = self.authentication_screen.get_username_input()
            else:
                self.password_input = self.authentication_screen.get_password_input()
            self.authentication_screen.handle_key_event(event)

        else:
            if hasattr(self, 'update_password') and self.update_password !=None and  self.update_password.update_status == True and current_screen == PASSWORD:
                self.update_password.handle_key_event(event)
            elif hasattr(self, 'host_name') and  self.host_name.update_status == True and current_screen == HOSTNAME:
                self.host_name.handle_key_event(event)
            else:
                self.authentication_screen.handle_key_event(event)

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

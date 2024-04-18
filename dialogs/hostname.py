import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig
from  system_controller.systemcontroler import SystemControler
import re
import warnings

warnings.filterwarnings("ignore")

class HostnameScreen:
    def __init__(self, screen_height, screen_width,app):
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.current_hostname = ""
        self.autheticated_parameter = True
        self.update_status = False
        self.shift_status = False
        self.system_controller  = SystemControler()
        self.logger_ = UdrLogger()
        self.setup_hostname_screen()

    def setup_hostname_screen(self):
        auth_screen_height = 10
        auth_screen_width = 40
        popup_y = (self.screen_height - auth_screen_height // 2) // 2
        popup_x = (self.screen_width - auth_screen_width) // 2
        self.hostname_screen = curses.newwin(auth_screen_height, auth_screen_width, popup_y, popup_x)

        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = max(int(0.3 * auth_screen_height), 1)
        popup_bottom_height = auth_screen_height - popup_top_height

        # Create windows for each partition within the pop-up window
        auth_top_win = self.hostname_screen.subwin(popup_top_height, auth_screen_width, popup_y, popup_x)
        auth_bottom_win = self.hostname_screen.subwin(popup_bottom_height, auth_screen_width,
                                                             popup_y + popup_top_height, popup_x)

        # Set background colors for each partition within the pop-up window
        auth_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        auth_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background

        # Add label to auth_top_win
        label_text = "Configure Hostname"
        label_x = (auth_screen_width - len(label_text)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        auth_top_win.addstr(label_y, label_x, label_text, curses.color_pair(4))

        username_label = "Hostname :  ["
        auth_bottom_win.addstr(1, 1, username_label, curses.color_pair(3))

        end_bracket_user = "]"
        auth_bottom_win.addstr(1, 35, end_bracket_user, curses.color_pair(3))

        # Add label to popup_bottom_win
        label_text_bottom_esc = "<Esc> Cancel"
        auth_bottom_win.addstr(5, 25, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_enter_ok = "<Enter> Ok"
        auth_bottom_win.addstr(5, 11, label_text_bottom_enter_ok, curses.color_pair(3))

        # Create username input box
        user_input_y = popup_y + popup_top_height + 1
        user_input_x = popup_x + 15
        self.current_hostname_win = curses.newwin(1, 21, user_input_y, user_input_x)
        self.current_hostname_win.refresh()
        

        curses.curs_set(1)
        self.hostname_screen.refresh()
        self.current_hostname = self.system_controller.get_hostname()
        self.logger_.log_info("current hostname value {}".format(self.current_hostname))
        self.current_hostname_win.addstr(0, 0, self.current_hostname, curses.color_pair(2))
        self.current_hostname_win.refresh()


    def set_cursor_position(self):
        """Set the cursor position based on the current input and status."""

        self.current_hostname_win.move(0, len(self.current_hostname))
        self.current_hostname_win.refresh()



    def clear(self):
        self.clear_input_field()
        if hasattr(self, 'hostname_screen') and self.hostname_screen != None:
            self.hostname_screen.clear()
            self.hostname_screen.refresh()
            self.hostname_screen = None
            curses.curs_set(0)


    def clear_input_field(self):
        if hasattr(self, 'current_password_win') and self.current_hostname_win != None:
            self.current_hostname_win.clear()
            self.current_hostname_win.refresh()
            self.current_hostname_win = None



    def get_username_input(self):
        return self.current_hostname


    def cehck_shift_char(self,next_char):
        symbol_char = {"1":"!" ,"2":"@","3":"#","4":"$","5":"%","6":"^","7":"&","8":"*","9":"(","0":")"}
        if self.shift_status:
            if next_char in symbol_char:
                self.shift_status = False
                return symbol_char[next_char]
            else:
                self.shift_status = False
                return next_char.title()
                
        else:
                return next_char

    def handle_key_event(self, event):
        pattern = re.compile(r'^[a-zA-Z0-9]$')
        if event.name == "backspace":
            if len(self.current_hostname) > 0:
                self.current_hostname = self.current_hostname[:-1]
                self.current_hostname_win.clear()
                self.current_hostname_win.bkgd(' ', curses.color_pair(2)) 
                self.current_hostname_win.addstr(0, 0, self.current_hostname, curses.color_pair(2))
                self.current_hostname_win.refresh()
                self.set_cursor_position()
 
        elif event.name == "enter":
            if len(self.current_hostname) >0:
                self.hostname_screen.clear()
                self.hostname_screen = None
                self.logger_.log_info("Create system config screen ")
                self.system_config.create_system_configuration()

        elif event.name == "shift":
            self.shift_status = True

        elif event.name in ["up","down"]:
            pass 

        elif len(event.name) == 1:
            self.logger_.log_info(" — event name  {} {}".format(event.name,len(self.current_hostname)))
            if event.name == "—" and   len(self.current_hostname) < 20:
                self.logger_.log_info("check condition of hostname {}".format(event.name))
                self.current_hostname += event.name
                self.current_hostname_win.addstr(0, 0, self.current_hostname, curses.color_pair(2))
                self.current_hostname_win.refresh()
                self.set_cursor_position()
            else:
                self.logger_.log_info("check else condition of hostname {}".format(event.name))
                char_value = self.cehck_shift_char(event.name)
                if pattern.match(char_value) and len(self.current_hostname) < 20:
                    self.current_hostname += char_value
                    self.current_hostname_win.addstr(0, 0, self.current_hostname, curses.color_pair(2))
                    self.current_hostname_win.refresh()
                    self.set_cursor_position()
                
                     

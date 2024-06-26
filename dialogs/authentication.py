import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

class AuthenticationScreen:
    def __init__(self, stdscr, screen_height, screen_width):
        self.stdscr = stdscr
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.username_input = ""
        self.password_input = ""
        self.current_status = "username"
        self.autheticated_parameter = True
        self.shift_status = False
        self.logger_ = UdrLogger(is_debug=True)
        self.setup_authentication_screen()

    def setup_authentication_screen(self):
        # Create a pop-up window
        auth_screen_height = 10
        auth_screen_width = 40
        popup_y = (self.screen_height - auth_screen_height // 2) // 2
        popup_x = (self.screen_width - auth_screen_width) // 2
        self.authentication_screen = curses.newwin(auth_screen_height, auth_screen_width, popup_y, popup_x)

        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = max(int(0.3 * auth_screen_height), 1)
        popup_bottom_height = auth_screen_height - popup_top_height

        # Create windows for each partition within the pop-up window
        auth_top_win = self.authentication_screen.subwin(popup_top_height, auth_screen_width, popup_y, popup_x)
        auth_bottom_win = self.authentication_screen.subwin(popup_bottom_height, auth_screen_width,
                                                             popup_y + popup_top_height, popup_x)

        # Set background colors for each partition within the pop-up window
        auth_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        auth_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background

        # Add label to auth_top_win
        label_text = "Authentication"
        label_x = (auth_screen_width - len(label_text)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        auth_top_win.addstr(label_y, label_x, label_text, curses.color_pair(4))

        username_label = "Username:  ["
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
        user_input_x = popup_x + 13
        self.username_win = curses.newwin(1, 20, user_input_y, user_input_x)
        self.username_win.refresh()

        # Print password label
        auth_bottom_win.addstr(3, 1, "Password:  [", curses.color_pair(3))
        auth_bottom_win.addstr(3, 35, end_bracket_user, curses.color_pair(3))

        # Create password input box
        password_input_y = user_input_y + 2
        self.password_win = curses.newwin(1, 20, password_input_y, user_input_x)
        self.password_win.refresh()

    

        curses.curs_set(1)
        self.authentication_screen.refresh()
        self.set_cursor_position()

    def set_cursor_position(self):
        """Set the cursor position based on the current input and status."""
        if self.current_status == "username":
            if hasattr(self, 'username_win') and self.username_win != None:
                self.username_win.move(0, len(self.username_input))
                self.username_win.refresh()
        elif self.current_status == "password":
            if hasattr(self, 'password_win') and self.password_win != None:
                self.password_win.move(0, len(self.password_input))
                self.password_win.refresh()

    def clear(self):
        
        self.authentication_screen.clear()
        self.authentication_screen.refresh()

    def clear_input_field(self):
        if hasattr(self, 'username_win') and self.username_win != None:
            self.username_win.clear()
            self.username_win = None 
        if hasattr(self, 'password_win') and self.password_win != None:
            self.password_win.clear()
            self.password_win = None

    def get_username_input(self):
        return self.username_input

    def get_password_input(self):
        return self.password_input

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
        if event.name == "backspace":
            if self.current_status == "username" and len(self.username_input) > 0:
                self.username_input = self.username_input[:-1]
                if hasattr(self, 'username_win') and self.username_win != None:
                    self.username_win.clear()
                    self.username_win.bkgd(' ', curses.color_pair(2)) 
                    self.username_win.addstr(0, 0, self.username_input, curses.color_pair(2))
                    self.username_win.refresh()
                    self.set_cursor_position()
            elif self.current_status == "password" and len(self.password_input) > 0:
                self.password_input = self.password_input[:-1]
                if hasattr(self, 'password_win') and self.password_win != None:
                    self.password_win.clear()
                    self.password_win.bkgd(' ', curses.color_pair(2)) 
                    self.password_win.addstr(0, 0, "*" * len(self.password_input), curses.color_pair(2))
                    self.password_win.refresh()
                    self.set_cursor_position()
        elif event.name == "enter":
            if len(self.username_input) >0 or len(self.password_input) >0:
                self.authentication_screen.clear()
                self.authentication_screen = None
                

        elif event.name == "tab":
            if  self.current_status == "username":
                self.current_status = "password"
                self.logger_.log_info("CURRENT PASSWORD FIED")
                self.set_cursor_position()
            elif self.current_status == "password":
                self.current_status = "username"
                self.logger_.log_info("CURRENT USERNAME FIED")
                self.set_cursor_position()
            
        elif event.name == "shift":
            self.shift_status = True 
        elif len(event.name) == 1:
            char_ = self.cehck_shift_char(event.name)
            if  self.current_status == "username" and len(self.username_input) < 19  :
                self.username_input += char_
                if hasattr(self, 'username_win') and self.username_win != None:
                    self.username_win.addstr(0, 0, self.username_input, curses.color_pair(2))
                    self.username_win.refresh()
                    self.set_cursor_position()
            if  self.current_status == "password" and  len(self.password_input) < 19  :
                self.password_input += char_
                if hasattr(self, 'password_win') and self.password_win != None:
                    self.password_win.addstr(0, 0, "*" * len(self.password_input), curses.color_pair(2))
                    self.password_win.refresh()
                    self.set_cursor_position()

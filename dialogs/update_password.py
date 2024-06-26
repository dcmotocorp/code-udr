import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig


class UpdatePasswordScreen:
    def __init__(self, screen_height, screen_width,app):
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.current_password = ""
        self.new_password = ""
        self.shift_status = False
        self.confirm_password = ""
        self.current_status = "current_password"
        self.update_status = False
        self.autheticated_parameter = True
        self.logger_ = UdrLogger(is_debug=True)
        self.setup_update_password_screen()

    def setup_update_password_screen(self):
        # Create a pop-up window
        auth_screen_height = 12
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
        label_text = "Configure Password"
        label_x = (auth_screen_width - len(label_text)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        auth_top_win.addstr(label_y, label_x, label_text, curses.color_pair(4))

        username_label = "Current Password:  ["
        auth_bottom_win.addstr(1, 1, username_label, curses.color_pair(3))

        end_bracket_user = "]"
        auth_bottom_win.addstr(1, 39, end_bracket_user, curses.color_pair(3))

        # Add label to popup_bottom_win
        label_text_bottom_esc = "<Esc> Cancel"
        auth_bottom_win.addstr(7, 25, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_enter_ok = "<Enter> Ok"
        auth_bottom_win.addstr(7, 11, label_text_bottom_enter_ok, curses.color_pair(3))

        # Create username input box
        user_input_y = popup_y + popup_top_height + 1
        user_input_x = popup_x + 21
        self.current_password_win = curses.newwin(1, 17, user_input_y, user_input_x)
        self.current_password_win.refresh()

        # Print password label
        auth_bottom_win.addstr(3, 1, "New Password:      [", curses.color_pair(3))
        auth_bottom_win.addstr(3, 39, end_bracket_user, curses.color_pair(3))

        auth_bottom_win.addstr(5, 1, "Confirm Password:  [", curses.color_pair(3))
        auth_bottom_win.addstr(5, 39, end_bracket_user, curses.color_pair(3))

        # Create password input box
        password_input_y = user_input_y + 2
        self.new_password_win = curses.newwin(1, 17, password_input_y, user_input_x)
        self.new_password_win.refresh()


        #conform password 
        conform_password_input_y = password_input_y +2 
        self.conform_password_win = curses.newwin(1, 17, conform_password_input_y, user_input_x)
        self.conform_password_win.refresh()


        curses.curs_set(1)
        self.authentication_screen.refresh()
        self.set_cursor_position()

    def clear(self):
        self.clear_all_input()
        if hasattr(self, 'authentication_screen') and self.authentication_screen != None:
            curses.curs_set(0)
            self.authentication_screen.clear()
            self.authentication_screen.refresh()
            self.authentication_screen = None
            

    def clear_all_input(self):
        if hasattr(self, 'conform_password_win') and self.conform_password_win != None:   
            self.conform_password_win.clear()
            self.conform_password_win = None 
        if hasattr(self, 'new_password_win') and self.new_password_win != None:
            self.new_password_win.clear()
            self.new_password_win  = None
        if hasattr(self, 'current_password_win') and self.current_password_win != None:
            self.current_password_win.clear()         
            self.current_password_win = None
    
    def get_username_input(self):
        return self.current_password

    def get_password_input(self):
        return self.new_password


    

    def handle_key_event(self, event):
        if event.name == "backspace":
            if self.current_status == "current_password"  and  len(self.current_password) >0:
                self.current_password = self.current_password[:-1]
                self.current_password_win.clear()
                self.current_password_win.bkgd(' ', curses.color_pair(2)) 
                self.current_password_win.addstr(0, 0, "*" * len(self.current_password), curses.color_pair(2))
                self.current_password_win.refresh()
                self.set_cursor_position()

            elif self.current_status == "current_new" and  len(self.new_password) >0:
                self.new_password = self.new_password[:-1]
                self.new_password_win.clear()
                self.new_password_win.bkgd(' ', curses.color_pair(2)) 
                self.new_password_win.addstr(0, 0, "*" * len(self.new_password), curses.color_pair(2))
                self.new_password_win.refresh()
                self.set_cursor_position()

            elif self.current_status == "conform_new" and len(self.confirm_password) >0:
                self.confirm_password = self.confirm_password[:-1]
                self.conform_password_win.clear()
                self.conform_password_win.bkgd(' ', curses.color_pair(2)) 
                self.conform_password_win.addstr(0, 0, "*" * len(self.confirm_password), curses.color_pair(2))
                self.conform_password_win.refresh()
                self.set_cursor_position()
        
        elif event.name == "enter":
            if len(self.current_password) >0 or len(self.new_password) >0:
                self.authentication_screen.clear()
                self.authentication_screen = None
                self.system_config.create_system_configuration()
        
        elif event.name == "shift":
            self.shift_status = True 

        elif event.name in ["up","down"]:
            pass 
        
        elif event.name == "tab":
            if  self.current_status == "current_password":
                self.current_status = "current_new"
                self.set_cursor_position()
            
            elif self.current_status == "current_new":
                self.current_status = "conform_new"
                self.set_cursor_position()

            elif self.current_status == "conform_new":
                self.current_status = "current_password"
                self.set_cursor_position()

        elif len(event.name) == 1:
            char_ = self.cehck_shift_char(event.name)
            
            if hasattr(self, 'current_password_win') and self.current_password_win != None and  self.current_status == "current_password" and len(self.current_password) < 16  :
                self.current_password += char_
                self.current_password_win.addstr(0, 0, "*" * len(self.current_password), curses.color_pair(2))
                
                self.current_password_win.refresh()
                self.set_cursor_position()
                
            elif hasattr(self, 'new_password_win') and self.new_password_win != None and self.current_status == "current_new" and  len(self.new_password) < 16  :
                self.new_password += char_
                self.new_password_win.addstr(0, 0, "*" * len(self.new_password), curses.color_pair(2))
                self.new_password_win.refresh()
                self.set_cursor_position()

            elif  hasattr(self, 'conform_password_win') and self.conform_password_win != None and self.current_status == "conform_new" and len(self.confirm_password) < 16:
                self.confirm_password += char_
                self.conform_password_win.addstr(0, 0, "*" * len(self.confirm_password), curses.color_pair(2))
                self.conform_password_win.refresh()
                self.set_cursor_position()

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
    
    def set_cursor_position(self):
        """Set the cursor position based on the current input and status."""

        if self.current_status == "current_password":
            self.current_password_win.move(0, len(self.current_password))
            self.current_password_win.refresh()
        
        elif self.current_status == "current_new":

            self.new_password_win.move(0, len(self.new_password))
            self.new_password_win.refresh()
        
        elif self.current_status == "conform_new":

            self.conform_password_win.move(0, len(self.confirm_password))
            self.conform_password_win.refresh()
        
        
        

                 

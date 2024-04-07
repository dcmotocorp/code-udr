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
        self.confirm_password = ""
        self.current_status = "current_password"
        self.autheticated_parameter = True
        self.logger_ = UdrLogger()
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
        auth_bottom_win.addstr(1, 35, end_bracket_user, curses.color_pair(3))

        # Add label to popup_bottom_win
        label_text_bottom_esc = "<Esc> Cancel"
        auth_bottom_win.addstr(7, 25, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_enter_ok = "<Enter> Ok"
        auth_bottom_win.addstr(7, 11, label_text_bottom_enter_ok, curses.color_pair(3))

        # Create username input box
        user_input_y = popup_y + popup_top_height + 1
        user_input_x = popup_x + 21
        self.current_password_win = curses.newwin(1, 20, user_input_y, user_input_x)
        self.current_password_win.refresh()

        # Print password label
        auth_bottom_win.addstr(3, 1, "New Password:      [", curses.color_pair(3))
        auth_bottom_win.addstr(3, 35, end_bracket_user, curses.color_pair(3))

        auth_bottom_win.addstr(5, 1, "Confirm Password:  [", curses.color_pair(3))
        auth_bottom_win.addstr(5, 35, end_bracket_user, curses.color_pair(3))

        # Create password input box
        password_input_y = user_input_y + 2
        self.new_password_win = curses.newwin(2, 20, password_input_y, user_input_x)
        self.new_password_win.refresh()


        #conform password 
        conform_password_input_y = password_input_y +2 
        self.conform_password_win = curses.newwin(2, 20, conform_password_input_y, user_input_x)
        self.conform_password_win.refresh()


        # Set placeholders for username and password fields
        username_placeholder = "Enter username"
        password_placeholder = "Enter password"
        self.current_password_win.addstr(0, 0, username_placeholder, curses.color_pair(3))
        self.new_password_win.addstr(0, 0, password_placeholder, curses.color_pair(3))
        self.current_password_win.refresh()
        self.new_password_win.refresh()

        curses.curs_set(1)
        self.authentication_screen.refresh()
        curses.curs_set(0)

    def clear(self):
        self.authentication_screen.clear()
        self.authentication_screen.refresh()
        self.authentication_screen = None

    def get_username_input(self):
        return self.current_password

    def get_password_input(self):
        return self.new_password

    def handle_key_event(self, event):
        if event.name == "backspace":
            if self.current_status == "current_password"  and  len(self.current_password) > 0:
                self.current_password = self.current_password[:-1]
                self.current_password_win.clear()
                self.current_password_win.addstr(0, 0, self.current_password, curses.color_pair(1))
                self.current_password_win.refresh()
            elif self.current_status == "current_new" and  len(self.new_password) > 0:
                self.new_password = self.new_password[:-1]
                self.new_password_win.clear()
                self.new_password_win.addstr(0, 0, "*" * len(self.new_password), curses.color_pair(1))
                self.new_password_win.refresh()
            elif self.current_status == "conform_new" and len(self.confirm_password) > 0:
                self.confirm_password = self.confirm_password[:-1]
                self.conform_password_win.clear()
                self.conform_password_win.addstr(0, 0, "*" * len(self.new_password), curses.color_pair(1))
                self.conform_password_win.refresh()
        
        elif event.name == "enter":
            self.logger_.log_info("Enter in the screen {} {}".format(self.current_password,self.new_password))
            if len(self.current_password) >0 or len(self.new_password) >0:
                self.authentication_screen.clear()
                self.authentication_screen = None
                self.logger_.log_info("Create system config screen ")
                self.system_config.create_system_configuration()

        elif event.name == "tab":
            if  self.current_status == "current_password":
                self.current_status = "current_new"
            elif self.current_status == "current_new":
                self.current_status = "conform_new"
            elif self.current_status == "conform_new":
                self.current_status = "current_password"

            self.logger_.log_info("switch event.name for the update passeord - {}".format(event.name))
        elif len(event.name) == 1:
            
            if  self.current_status == "current_password" and len(self.current_password) < 10  :
                self.logger_.log_info("event.name - {} current name {} iuser input {}".format(event.name,self.current_status,self.current_password))
                self.current_password += event.name
                self.current_password_win.addstr(0, 0, self.current_password, curses.color_pair(1))
                self.current_password_win.refresh()
            if  self.current_status == "current_new" and  len(self.new_password) < 10  :
                self.logger_.log_info("current_new.name - {} current name {} iuser input {}".format(event.name,self.current_status,self.current_password))
                self.new_password += event.name
                self.new_password_win.addstr(0, 0, "*" * len(self.new_password), curses.color_pair(1))
                self.new_password_win.refresh()
            if  self.current_status == "conform_new" and len(self.confirm_password) < 10:
                self.confirm_password += event.name
                self.conform_password_win.addstr(0, 0, "*" * len(self.confirm_password), curses.color_pair(1))
                self.conform_password_win.refresh()
                 

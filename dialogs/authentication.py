import curses
from logs.udr_logger import UdrLogger

class AuthenticationScreen:
    def __init__(self, stdscr, screen_height, screen_width):
        self.stdscr = stdscr
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.username_input = ""
        self.password_input = ""
        self.current_status = "username"
        self.logger_ = UdrLogger()
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
        self.password_win = curses.newwin(2, 20, password_input_y, user_input_x)
        self.password_win.refresh()

        # Set placeholders for username and password fields
        username_placeholder = "Enter username"
        password_placeholder = "Enter password"
        self.username_win.addstr(0, 0, username_placeholder, curses.color_pair(3))
        self.password_win.addstr(0, 0, password_placeholder, curses.color_pair(3))
        self.username_win.refresh()
        self.password_win.refresh()

        curses.curs_set(1)
        self.authentication_screen.refresh()
        curses.curs_set(0)

    def clear(self):
        self.authentication_screen.clear()
        self.authentication_screen.refresh()

    def get_username_input(self):
        return self.username_input

    def get_password_input(self):
        return self.password_input

    def handle_key_event(self, event):
        if event.name == "backspace":
            if len(self.username_input) > 0:
                self.username_input = self.username_input[:-1]
                self.username_win.clear()
                self.username_win.addstr(0, 0, self.username_input, curses.color_pair(1))
                self.username_win.refresh()
            elif len(self.password_input) > 0:
                self.password_input = self.password_input[:-1]
                self.password_win.clear()
                self.password_win.addstr(0, 0, "*" * len(self.password_input), curses.color_pair(1))
                self.password_win.refresh()
        elif event.name == "enter":
            return "enter"

        elif event.name == "tab":
            if  self.current_status == "username":
                self.current_status = "password"
            elif self.current_status == "password":
                self.current_status = "username"
            self.logger_.log_info("switch event.name - {}".format(event.name))
        elif len(event.name) == 1:
            
            if  self.current_status == "username" and len(self.username_input) < 20  :
                self.logger_.log_info("event.name - {} current name {} iuser input {}".format(event.name,self.current_status,self.username_input))
                self.username_input += event.name
                self.username_win.addstr(0, 0, self.username_input, curses.color_pair(1))
                self.username_win.refresh()
            if  self.current_status == "password" and  len(self.password_input) < 20  :
                self.logger_.log_info("password.name - {} current name {} iuser input {}".format(event.name,self.current_status,self.username_input))
                self.password_input += event.name
                self.password_win.addstr(0, 0, "*" * len(self.password_input), curses.color_pair(1))
                self.password_win.refresh()

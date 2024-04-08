import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig


class HostnameScreen:
    def __init__(self, screen_height, screen_width,app):
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.current_hostname = ""
        self.autheticated_parameter = True
        self.update_status = False
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
        self.current_password_win = curses.newwin(1, 20, user_input_y, user_input_x)
        self.current_password_win.refresh()

        curses.curs_set(1)
        self.hostname_screen.refresh()
        curses.curs_set(0)

    def clear(self):
        self.clear_input_field()
        self.hostname_screen.clear()
        self.hostname_screen.refresh()
        self.hostname_screen = None


    def clear_input_field(self):
        self.current_password_win.clear()
        self.current_password_win.refresh()
        self.current_password_win = None



    def get_username_input(self):
        return self.current_hostname



    def handle_key_event(self, event):
        if event.name == "backspace":
            if len(self.current_hostname) > 0:
                self.current_hostname = self.current_hostname[:-1]
                self.current_password_win.clear()
                self.current_password_win.addstr(0, 0, self.current_hostname, curses.color_pair(1))
                self.current_password_win.refresh()
 
        elif event.name == "enter":
            if len(self.current_hostname) >0:
                self.hostname_screen.clear()
                self.hostname_screen = None
                self.logger_.log_info("Create system config screen ")
                self.system_config.create_system_configuration()

        elif len(event.name) == 1:
            if  len(self.current_hostname) < 10  :
                self.current_hostname += event.name
                self.current_password_win.addstr(0, 0, self.current_hostname, curses.color_pair(1))
                self.current_password_win.refresh()
            
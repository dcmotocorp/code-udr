import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig
from constant import KEY_UP,KEY_DOWN,CONFIGURE_MANAGEMENT_NETWORK_SERVICE,OBTAIN_IP_AUTOMATIC,MANUALLY_IP_AUTOMATIC,MANUALLY_DNS_AUTOMATIC,OBTAIN_DNS_AUTOMATIC

class DNSScreen:
    def __init__(self, screen_height, screen_width,app):
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.current_ssh = ""
        self.autheticated_parameter = True
        self.update_status = False
        self.current_seleected_parameter = None
        self.current_selected_label_index = 0
        self.labels = [OBTAIN_DNS_AUTOMATIC.format(""), MANUALLY_DNS_AUTOMATIC.format("")]
        self.normal_color_pair = curses.color_pair(3) 
        self.selected_color_pair = curses.color_pair(5)
        self.logger_ = UdrLogger()
        self.selected_index= 0
        self.primary = "192.168.1.1"
        self.secondary =  "192.168.1.1"
        self.setup_network_adaptor_screen()

    def setup_network_adaptor_screen(self):
        auth_screen_height = 15
        auth_screen_width = 50
        popup_y = (self.screen_height - auth_screen_height // 2) // 2
        popup_x = (self.screen_width - auth_screen_width) // 2
        self.hostname_screen = curses.newwin(auth_screen_height, auth_screen_width, popup_y, popup_x)

        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = max(int(0.3 * auth_screen_height), 1)
        popup_bottom_height = auth_screen_height - popup_top_height

        # Create windows for each partition within the pop-up window
        auth_top_win = self.hostname_screen.subwin(popup_top_height, auth_screen_width, popup_y, popup_x)
        self.auth_bottom_win = self.hostname_screen.subwin(popup_bottom_height, auth_screen_width,
                                                             popup_y + popup_top_height, popup_x)

        # Set background colors for each partition within the pop-up window
        auth_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        self.auth_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background


        # Add label to auth_top_win
        label_x = (auth_screen_width - len(CONFIGURE_MANAGEMENT_NETWORK_SERVICE)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        auth_top_win.addstr(label_y, label_x, CONFIGURE_MANAGEMENT_NETWORK_SERVICE, curses.color_pair(4))
        

        # Add labels to popup_bottom_win
        for index, label in enumerate(self.labels):
            color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
            self.auth_bottom_win.addstr( 2+ index, 5, label, color_pair)


        # Add label to popup_bottom_win
        label_text_bottom_esc = "<Space> Selection"
        self.auth_bottom_win.addstr(9, 1, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_esc = "<Esc> Cancel"
        self.auth_bottom_win.addstr(9, 36, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_enter_ok = "<Enter> Ok"
        self.auth_bottom_win.addstr(9, 23, label_text_bottom_enter_ok, curses.color_pair(3))
        
        # ad ip config 
        ip_adrress_label = "Primary DNS Server :  [ {}     ]".format(self.primary)
        self.auth_bottom_win.addstr(5, 8, ip_adrress_label, curses.color_pair(3))

        mask_adrress_label = "Secondary DNS Server :[ {}     ]".format(self.secondary)
        self.auth_bottom_win.addstr(6, 8, mask_adrress_label, curses.color_pair(3))


    
        auth_top_win.refresh()
        self.auth_bottom_win.refresh()

    def clear(self):
        if hasattr(self, 'hostname_screen') and self.hostname_screen != None:
            self.hostname_screen.clear()
            self.hostname_screen.refresh()
            self.hostname_screen = None

    def get_username_input(self):
        return self.current_ssh
    
    def handle_arrow_key(self, key):
    
        if key.name == "space":
            if self.selected_index == 0:
                 self.selected_index = 1
            else:
                 self.selected_index = 0
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                self.auth_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.auth_bottom_win.refresh()
        self.setup_network_adaptor_screen()


            




import curses
from constant import SYSTEM_CONFIG_LABEL, PASSWORD, HOSTNAME, SSH,LOCK_DOWN_MODE


class SystemConfig:
    def __init__(self, screen_height, screen_width,app=None):
        self.popup_win = None
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
       
    def create_system_configuration(self):
        sc_config_height, sc_config_width = int(self.screen_height*0.98) , int(self.screen_width*0.99)
        sc_config_x = int(self.screen_width*0.015)
        sc_config_y = int(self.screen_height*0.025)
        
        self.system_configuration_screen = curses.newwin(sc_config_height, sc_config_width, sc_config_y, sc_config_x)

        # Calculate dimensions for the two partitions within the pop-up window
        sc_config_top_height = max(int(0.6 * sc_config_height), 1)
        sc_config_bottom_height = sc_config_height - sc_config_top_height

        # Create windows for each partition within the pop-up window
        sc_config_top_win = self.system_configuration_screen.subwin(sc_config_top_height, sc_config_width, sc_config_y, sc_config_x)
        sc_config_bottom_win = self.system_configuration_screen.subwin(sc_config_bottom_height, sc_config_width, sc_config_y + sc_config_top_height, sc_config_x)

        # Set background colors for each partition within the pop-up window
        sc_config_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        sc_config_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background
        
        

        #system configuration label 
        sc_config_top_win.addstr(1, 2, SYSTEM_CONFIG_LABEL, curses.color_pair(4))
        sc_config_top_win.addstr(3, 2, PASSWORD, curses.color_pair(4))
        sc_config_top_win.addstr(4, 2, HOSTNAME, curses.color_pair(4))
        sc_config_top_win.addstr(5, 2, SSH, curses.color_pair(4))
        sc_config_top_win.addstr(6, 2, LOCK_DOWN_MODE, curses.color_pair(4))

        
        self.system_configuration_screen.refresh()
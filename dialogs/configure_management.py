



import curses
from constant import SYSTEM_CONFIG_LABEL, PASSWORD, HOSTNAME, SSH,LOCK_DOWN_MODE,MANAGEMENT_INTERFACE,RESET_SYSTEM_CONFIG,KEY_DOWN,KEY_UP
import curses
from logs.udr_logger import UdrLogger

class SystemConfig:
    def __init__(self, screen_height, screen_width, app=None):
        self.popup_win = None
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.logger_ = UdrLogger()
        self.active_status = True
        self.update_password_screen = False
        self.selected_index = 0  # Index of the currently selected label
        self.labels = [ PASSWORD, HOSTNAME, MANAGEMENT_INTERFACE, SSH, LOCK_DOWN_MODE, RESET_SYSTEM_CONFIG]
        self.label_count = len(self.labels)
        self.selected_color_pair = curses.color_pair(5)  # Color pair for selected label
        self.normal_color_pair = curses.color_pair(4)    # Color pair for normal label
        self.sys_config ={PASSWORD:["Set/Change","To prevent unautherized access to this system use complex","password with minimum lenth of 14 characters"],
                            HOSTNAME: ["Set/Change","To prevent unautherized access to this system use complex","password with minimum lenth of 14 characters"] ,
                            MANAGEMENT_INTERFACE:["Configure Management Interface","To prevent unautherized access to this system use complex","password with minimum lenth of 14 characters"] ,
                            SSH:["SSH","To prevent unautherized access to this system use complex"," password with minimum lenth of 14 characters"],
                            LOCK_DOWN_MODE:["LOCK_DOWN_MODE","To prevent unautherized access to this system use complex","password with minimum lenth of 14 characters"],
                            RESET_SYSTEM_CONFIG:["RESET_SYSTEM_CONFIG","To prevent unautherized access to this system use complex","password with minimum lenth of 14 characters"]}
        
    def create_system_configuration(self):
        sc_config_height, sc_config_width = int(self.screen_height * 0.98), int(self.screen_width * 0.99)
        sc_config_x = int(self.screen_width * 0.015)
        sc_config_y = int(self.screen_height * 0.025)

        self.system_configuration_screen = curses.newwin(sc_config_height, sc_config_width, sc_config_y, sc_config_x)

        # Calculate dimensions for the two partitions within the pop-up window
        sc_config_top_height = max(int(0.6 * sc_config_height), 1)
        sc_config_bottom_height = sc_config_height - sc_config_top_height

        # Create windows for each partition within the pop-up window
        self.sc_config_top_win = self.system_configuration_screen.subwin(sc_config_top_height, sc_config_width, sc_config_y, sc_config_x)
        self.sc_config_bottom_win = self.system_configuration_screen.subwin(sc_config_bottom_height, sc_config_width, sc_config_y + sc_config_top_height, sc_config_x)

        # Set background colors for each partition within the pop-up window
        self.sc_config_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        self.sc_config_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background

        self.sc_config_top_win.addstr(3 , 5, SYSTEM_CONFIG_LABEL, self.normal_color_pair)

        # System configuration labels
        for index, label in enumerate(self.labels):
            color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
            self.sc_config_top_win.addstr( 5+ index, 5, label, color_pair)

        self.system_configuration_screen.refresh()
        # Create the square
        square_height =  22
        square_width =  int(self.screen_width * 0.45)  # Adjust the width as needed
        square_x = int(self.screen_width * 0.4)
        square_y =  2
        self.square_win = curses.newwin(square_height, square_width, square_y, square_x)
        self.square_win.bkgd(' ', curses.color_pair(1))  # Set background color to match screen background
        self.square_win.box() 
        
        

        #setup new tab
        current_label = self.labels[self.selected_index]
        label_value = self.sys_config.get(current_label) 
        self.square_win.addstr(1, 2, label_value[0], self.normal_color_pair)
        self.square_win.addstr(3, 2, label_value[1], self.normal_color_pair)
        self.square_win.addstr(4, 2, label_value[2], self.normal_color_pair)
        self.square_win.refresh() 

        #for the bottom part set the label
        label_text_bottom_enter_ok = "<Enter> Ok"
        self.sc_config_bottom_win.addstr(sc_config_top_height-10, 2, label_text_bottom_enter_ok, curses.color_pair(3))
        self.sc_config_bottom_win.refresh()

        label_text_bottom_esc_log_out = "<Esc> Log out"
        self.sc_config_bottom_win.addstr(sc_config_top_height-10, sc_config_width-15, label_text_bottom_esc_log_out, curses.color_pair(3))
        self.sc_config_bottom_win.refresh()

    def set_sytem_config_screen_dark(self):
        self.sc_config_top_win.bkgd(' ', curses.color_pair(0))  # Yellow background
        self.sc_config_bottom_win.bkgd(' ', curses.color_pair(0))  # Grey background
        
        self.update_color_font()
        
        self.sc_config_top_win.refresh()
        self.sc_config_bottom_win.refresh()


    def update_color_font(self):

        sc_config_height, sc_config_width = int(self.screen_height * 0.98), int(self.screen_width * 0.99)
        sc_config_top_height = max(int(0.6 * sc_config_height), 1)
        
        self.sc_config_top_win.addstr(3 , 5, SYSTEM_CONFIG_LABEL, curses.color_pair(0))
        
        for index, label in enumerate(self.labels):
            self.sc_config_top_win.addstr( 5+ index, 5, label, curses.color_pair(0))
        
        label_text_bottom_enter_ok = "<Enter> Ok"
        self.sc_config_bottom_win.addstr(sc_config_top_height-10, 2, label_text_bottom_enter_ok, curses.color_pair(0))
    

        label_text_bottom_esc_log_out = "<Esc> Log out"
        self.sc_config_bottom_win.addstr(sc_config_top_height-10, sc_config_width-15, label_text_bottom_esc_log_out, curses.color_pair(0))
                

    def handle_arrow_key(self, key):
        self.sc_config_top_win.clear()
        self.sc_config_top_win = None
        
        
        sc_config_height, sc_config_width = int(self.screen_height * 0.98), int(self.screen_width * 0.99)
        sc_config_x = int(self.screen_width * 0.015)
        sc_config_y = int(self.screen_height * 0.025)

        # Calculate dimensions for the two partitions within the pop-up window
        sc_config_top_height = max(int(0.6 * sc_config_height), 1)
        sc_config_bottom_height = sc_config_height - sc_config_top_height

        # Create windows for each partition within the pop-up window
        self.sc_config_top_win = self.system_configuration_screen.subwin(sc_config_top_height, sc_config_width, sc_config_y, sc_config_x)
    
        # Set background colors for each partition within the pop-up window
        self.sc_config_top_win.bkgd(' ', curses.color_pair(1))
        
        
        if key ==  KEY_UP:
            self.selected_index = max(0, self.selected_index - 1)            
              # Yellow background
            
            
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                self.sc_config_top_win.addstr(5 + index, 5, label, color_pair)
            


            current_label = self.labels[self.selected_index]
            label_value = self.sys_config.get(current_label) 
            self.square_win.addstr(1, 2, label_value[0], self.normal_color_pair)
            self.square_win.addstr(3, 2, label_value[1], self.normal_color_pair)
            self.square_win.addstr(4, 2, label_value[2], self.normal_color_pair)
            self.square_win.refresh() 

            self.sc_config_top_win.refresh()

            

        elif key == KEY_DOWN:
            self.selected_index = min(self.label_count - 1, self.selected_index + 1)
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                self.sc_config_top_win.addstr(5 + index, 5, label, color_pair)
            
            current_label = self.labels[self.selected_index]
            label_value = self.sys_config.get(current_label) 
            self.square_win.addstr(1, 2, label_value[0], self.normal_color_pair)
            self.square_win.addstr(3, 2, label_value[1], self.normal_color_pair)
            self.square_win.addstr(4, 2, label_value[2], self.normal_color_pair)
            self.square_win.refresh()

            self.sc_config_top_win.refresh()
        self.create_system_configuration()

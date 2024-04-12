import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig
from constant import KEY_UP,KEY_DOWN,SELECT_MANAGEMENT_NETWORK_SERVICE,OBTAIN_IP_AUTOMATIC,MANUALLY_IP_AUTOMATIC
from copy import deepcopy
import json 

class NetworkAdaptorScreen:
    def __init__(self, screen_height, screen_width,app):
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.current_ssh = ""
        self.autheticated_parameter = True
        self.update_status = False
        self.current_seleected_parameter = None
        self.current_selected_label_index = 0
        self.labels = [["[{}] N1C1","00.01.D1:F3:55:2D","Connected"],["[{}] N1C2","00.01.D5:F3:55:2D","Connected"],["[{}] N1C3","00.01.D1:F3:55:2D","Connected"]]
        self.current_label = []
        self.normal_color_pair = curses.color_pair(3) 
        self.selected_color_pair = curses.color_pair(5)
        self.logger_ = UdrLogger()
        self.selected_index= 0
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
        label_x = (auth_screen_width - len(SELECT_MANAGEMENT_NETWORK_SERVICE)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        auth_top_win.addstr(label_y, label_x, SELECT_MANAGEMENT_NETWORK_SERVICE, curses.color_pair(4))
        

        self.auth_bottom_win.addstr( 1, 5, "Name",self.normal_color_pair)
        self.auth_bottom_win.addstr( 1, 15,"Mac Address",self.normal_color_pair)
        self.auth_bottom_win.addstr( 1, 35, "Status",self.normal_color_pair)

        # Add labels to popup_bottom_win
        for index, label in enumerate(self.labels):
            color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
            self.auth_bottom_win.addstr( 2+ index, 5, label[0].format(""), color_pair)
            self.auth_bottom_win.addstr( 2+ index, 15, label[1], color_pair)
            self.auth_bottom_win.addstr( 2+ index, 35, label[2], color_pair)


        # Add label to popup_bottom_win
        label_text_bottom_esc = "<Space> Selection"
        self.auth_bottom_win.addstr(9, 1, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_esc = "<Esc> Cancel"
        self.auth_bottom_win.addstr(9, 36, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_enter_ok = "<Enter> Ok"
        self.auth_bottom_win.addstr(9, 23, label_text_bottom_enter_ok, curses.color_pair(3))
        
        auth_top_win.refresh()
        self.auth_bottom_win.refresh()
        curses.curs_set(0)

    def clear(self):
        if hasattr(self, 'hostname_screen') and self.hostname_screen != None:
            self.hostname_screen.clear()
            self.hostname_screen.refresh()
            self.hostname_screen = None

    def get_username_input(self):
        return self.current_ssh
    
    def handle_arrow_key(self, key):
        
        if key.name =="up":
            if self.selected_index == 0:
                self.selected_index =0
            else :
                self.selected_index = self.selected_index - 1
            if len(self.current_label)>0:
                data = self.current_label
            else:
                test_daat = self.labels 
                tem = []
                for test in test_daat:
                    test[0] = test[0].format("")
                    tem.append(test)
                data = tem
            self.logger_.log_info("up data login info {}".format(json.dumps(data)))
            for index, label in enumerate(data):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                self.auth_bottom_win.addstr( 2+ index, 5, label[0], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 15, label[1], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 35, label[2], color_pair)
            self.auth_bottom_win.refresh()
        
        elif key.name =="down":
            if len(self.labels)-1 == self.selected_index:
                self.selected_index =len(self.labels)-1
            else :
                 self.selected_index += 1
            
            if len(self.current_label)>0:
                data = self.current_label    
            else:
                test_daat = self.labels 
                tem = []
                for test in test_daat:
                    test[0] = test[0].format("")
                    tem.append(test)
                data = tem
            self.logger_.log_info("down data login info {}".format(json.dumps(data)))
            for index, label in enumerate(data):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                self.auth_bottom_win.addstr( 2+ index, 5, label[0], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 15, label[1], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 35, label[2], color_pair)
            self.auth_bottom_win.refresh()

        if key.name == "space":
            self.current_label = []
            
            test_daat = self.labels 
            self.logger_.log_info("current login info self.selected_index{}".format(self.selected_index))
            for index, label in enumerate(test_daat):
                if index == self.selected_index:
                    c= []
                    for index,_tet in enumerate(label):
                        if index ==0:
                            ceo = _tet.format("0")
                            c.append(ceo)
                        else:
                            c.append(_tet)                
                    self.current_label.append(c)
                else:
                    label[0] = label[0].format("")
                    self.current_label.append(label)
                    
                
                


            
            self.logger_.log_info("current login info self.current_label{}".format(json.dumps(self.current_label)))
            for index, label in enumerate(self.current_label):
            
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                self.auth_bottom_win.addstr( 2+ index, 5, label[0], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 15, label[1], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 35, label[2], color_pair)
            self.auth_bottom_win.refresh()
            # self.setup_network_adaptor_screen()


            

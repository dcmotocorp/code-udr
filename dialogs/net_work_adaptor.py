import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig
from constant import KEY_UP,KEY_DOWN,SELECT_MANAGEMENT_NETWORK_SERVICE,OBTAIN_IP_AUTOMATIC,MANUALLY_IP_AUTOMATIC
from copy import deepcopy
from system_controller.systemcontroler import SystemControler
import json 
from data.database import UserDatabase

class NetworkAdaptorScreen:
    def __init__(self, screen_height, screen_width,app):
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.current_ssh = ""
        self.autheticated_parameter = True
        self.update_status = False
        self.current_seleected_parameter = None
        self.current_selected_label_index = None
        self.labels = [["N1C1","00.01.D1:F3:55:2D","Connected"],["N1C2","00.01.D5:F3:55:2D","Connected"],["N1C3","00.01.D1:F3:55:2D","Connected"]]
        self.current_label = []
        self.starting_state =True
        self.system_controller = SystemControler()
        self.normal_color_pair = curses.color_pair(3) 
        self.selected_color_pair = curses.color_pair(5)
        self.user_data_base = UserDatabase()
        self.logger_ = UdrLogger(is_debug=True)
        self.selected_index= 0
        self.get_data_from_source()
        self.setup_network_adaptor_screen()

    def get_data_from_source(self):
        data = self.system_controller.get_management_interface_details()
        response = self.remove_duplicate_data(data)
        self.logger_.log_info("source data {}".format(json.dumps(response)))
        self.set_source_data(response)
        self.get_selected_interface_data()
    
    def get_selected_interface_data(self):
        data =  self.user_data_base.get_interfaces_data("MGMT_INTERFACE")
        self.logger_.log_info("data mgmt data {}".format(json.dumps(data)))
        self.logger_.log_info("data mgmt data 2 {}".format(json.dumps(self.labels)))
        
        if data and len(data)>0:
            for index,_rs in enumerate(self.labels):
                self.logger_.log_info("data[2] mgmt data {} {}".format(data[2],_rs[0]))
                if data[2] == _rs[0]:
                    self.logger_.log_info("index mgmt index {}".format(index))
                    self.current_selected_label_index = index
                    self.selected_index = index

    def set_network_data(self):
        inetrface = self.get_current_interface()
        if inetrface is not None:
            self.system_controller.set_management_interface(inetrface)
        
    def set_source_data(self,data):
        resposne_data = []
        for __data in data:
            tem_list = []
            tem_list.append(__data.get('interface'))
            tem_list.append(__data.get('macAddress'))
            tem_list.append(__data.get('state'))
            resposne_data.append(tem_list) 
        self.logger_.log_info("source data {}".format(json.dumps(resposne_data)))
        self.labels = resposne_data
    
    def remove_duplicate_data(self,response):
        key_list = []
        resposne_updated = []
        for data in response:
            if data.get('interface') not in key_list:
                key_list.append(data.get('interface'))
                resposne_updated.append(data)
        return  resposne_updated  
         
    def get_current_interface(self):
        current_index = self.current_selected_label_index
        self.logger_.log_info("current_index data current_index {}".format(current_index))
        if current_index is not None:
            cselected_list = self.labels[current_index]
            self.logger_.log_info("cselected_list data cselected_list {}".format(cselected_list))
            return cselected_list[0]

    
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

        if self.current_selected_label_index and self.starting_state ==True:
            self.starting_state = False 
            for index, label in enumerate(self.labels):
                # color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_selected_label_index ==index:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]",  self.selected_color_pair)
                    self.auth_bottom_win.addstr( 2+ index, 5, label[0], self.selected_color_pair)
                    self.auth_bottom_win.addstr( 2+ index, 15, label[1], self.selected_color_pair)
                    self.auth_bottom_win.addstr( 2+ index, 35, label[2], self.selected_color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", self.normal_color_pair)
                    self.auth_bottom_win.addstr( 2+ index, 5, label[0], self.normal_color_pair)
                    self.auth_bottom_win.addstr( 2+ index, 15, label[1], self.normal_color_pair)
                    self.auth_bottom_win.addstr( 2+ index, 35, label[2], self.normal_color_pair)
            
        else:        
            # Add labels to popup_bottom_win
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_selected_label_index ==index:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                self.auth_bottom_win.addstr( 2+ index, 5, label[0], color_pair)
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
      
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if index == self.current_selected_label_index :
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                self.auth_bottom_win.addstr( 2+ index, 5, label[0], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 15, label[1], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 35, label[2], color_pair)
            self.auth_bottom_win.refresh()
        
        elif key.name =="down":
            if len(self.labels)-1 == self.selected_index:
                self.selected_index =len(self.labels)-1
            else :
                 self.selected_index += 1
            
           
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if index == self.current_selected_label_index :
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                self.auth_bottom_win.addstr( 2+ index, 5, label[0], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 15, label[1], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 35, label[2], color_pair)
            self.auth_bottom_win.refresh()

        if key.name == "space":
            
            self.current_selected_label_index = self.selected_index
            for index, label in enumerate(self.labels):
            
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if index == self.current_selected_label_index :
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                self.auth_bottom_win.addstr( 2+ index, 5, label[0], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 15, label[1], color_pair)
                self.auth_bottom_win.addstr( 2+ index, 35, label[2], color_pair)
            self.auth_bottom_win.refresh()
            # self.setup_network_adaptor_screen()


            

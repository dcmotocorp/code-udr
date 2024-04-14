import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig
from constant import KEY_UP,KEY_DOWN,CONFIGURE_MANAGEMENT_NETWORK_SERVICE,OBTAIN_IP_AUTOMATIC,MANUALLY_IP_AUTOMATIC
from system_controller.systemcontroler import SystemControler
import warnings
import json 
from data.database import UserDatabase


warnings.filterwarnings("ignore")

class IPConfigurationScreen:
    def __init__(self, screen_height, screen_width,app):
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.current_ssh = ""
        self.autheticated_parameter = True
        self.update_status = False
        self.current_seleected_parameter = None
        self.current_selected_label_index = 0
        self.labels = [OBTAIN_IP_AUTOMATIC, MANUALLY_IP_AUTOMATIC]
        self.normal_color_pair = curses.color_pair(3) 
        self.selected_color_pair = curses.color_pair(5)
        self.logger_ = UdrLogger()
        self.selected_index= 0
        self.system_controller = SystemControler()
        self.ip_address = "192.168.1.1"
        self.sub_mask =  "192.168.1.1"
        self.gate_Way =  "192.168.1.1"
        self.input_current_index_status="ip"
        self.user_data_base = UserDatabase()
        self.get_default_Setting()
        self.set_data()
        self.setup_network_adaptor_screen()

    def get_default_Setting(self):
        data =  self.user_data_base.get_user_settings(self.app.username_input)
        users = self.user_data_base.select_all_users()
        
        self.logger_.log_info("==========data {}".format(json.dumps(data)))
        self.logger_.log_info("==========users {}".format(json.dumps(users)))





    def set_data(self):
        ip,mask,gate_way= self.system_controller.get_network_info_su_de()
        self.ip_address = ip 
        self.sub_mask = mask
        self.gate_Way = gate_way

    def set_up_in_address_field(self):
        # ad ip config 
        auth_screen_height = 15
        auth_screen_width = 50
        popup_y = (self.screen_height - auth_screen_height // 2) // 2
        popup_x = (self.screen_width - auth_screen_width) // 2
        popup_top_height = max(int(0.3 * auth_screen_height), 1)
        popup_bottom_height = auth_screen_height - popup_top_height


        in_win_height = popup_y + popup_top_height +5
        ip_input_x = popup_x + 6
        self.ip_address_win = curses.newwin(1, 15,in_win_height , ip_input_x)
        self.ip_address_win.refresh()
        ip_adrress_label = "IP Address :"
        self.ip_address_win.addstr(0,0, ip_adrress_label, curses.color_pair(0))
        self.ip_address_win.refresh()

        mask_adrress_label = "Subnet Mask :     [ {}     ]".format(self.sub_mask)
        self.auth_bottom_win.addstr(6, 8, mask_adrress_label, curses.color_pair(3))

        getway_label = "Default Getway :  [ {}         ]".format(self.gate_Way)
        self.auth_bottom_win.addstr(7, 8, getway_label, curses.color_pair(3))
         

        


        self.auth_bottom_win.refresh()

    
    def setup_network_adaptor_screen(self):
        auth_screen_height = 15
        auth_screen_width = 50
        popup_y = (self.screen_height - auth_screen_height // 2) // 2
        popup_x = (self.screen_width - auth_screen_width) // 2
        self.hostname_screen = curses.newwin(auth_screen_height, auth_screen_width, popup_y, popup_x)

        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = max(int(0.3 * auth_screen_height), 1)
        popup_bottom_height = auth_screen_height - popup_top_height
        
        
        #  # Create windows for each partition within the pop-up window
        

        
        
        
        
        self.in_config = curses.newwin(1, 20, popup_y + popup_top_height, popup_x+10)
        self.in_config.refresh()
        
        curses.curs_set(1)
        

        self.in_config.addstr(0, 1, "test", curses.color_pair(1))
        self.in_config.refresh()

        self.auth_top_win = self.hostname_screen.subwin(popup_top_height, auth_screen_width, popup_y, popup_x)
        self.auth_bottom_win = self.hostname_screen.subwin(popup_bottom_height, auth_screen_width,
                                                             popup_y + popup_top_height, popup_x)

        # Set background colors for each partition within the pop-up window
        self.auth_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        self.auth_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background
        self.auth_top_win.refresh()
        self.auth_bottom_win.refresh()
    
        

    def set_manually_ip(self):
        self.system_controller.set_ip_configuration_manual(self.ip_address,self.sub_mask,self.gate_Way)
         
    def set_ip_address_automatic(self):
        self.system_controller.setup_ip_configuration(self.ip_address,self.sub_mask,self.gate_Way)
        
    def clear(self):
        if hasattr(self, 'hostname_screen') and self.hostname_screen != None:
            self.hostname_screen.clear()
            self.hostname_screen.refresh()
            self.hostname_screen = None

    def get_username_input(self):
        return self.current_ssh
    
    def handle_arrow_key(self, key):
    
        if key.name == "up":
            
            if self.selected_index == 1:
                 self.selected_index = 0
            else:
                 self.selected_index = 0
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_seleected_parameter == index:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                
 

                self.auth_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.auth_bottom_win.refresh()
            if self.current_seleected_parameter ==1:
                self.set_up_in_address_field()
            else:
                self.setup_network_adaptor_screen() 

        elif key.name =="down":
            
            if self.selected_index == 0:
                 self.selected_index = 1
            else:
                 self.selected_index = 1
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_seleected_parameter == index:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
    
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
            
                self.auth_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.auth_bottom_win.refresh()
            if self.current_seleected_parameter ==1:
                self.set_up_in_address_field()
            else:
                self.setup_network_adaptor_screen()

        elif key.name == "space":
            self.current_seleected_parameter = self.selected_index
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_seleected_parameter == index:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                    
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
            self.auth_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.auth_bottom_win.refresh()
            if self.current_seleected_parameter ==1:
                        self.set_up_in_address_field()
            else:
                self.setup_network_adaptor_screen()

        elif len(event.name) == 1:
            if self.input_current_index_status=="ip":
                self.ip_address =1
            


            
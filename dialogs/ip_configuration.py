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
        self.starting_state =True
        self.input_current_index_status="ip"
        self.user_data_base = UserDatabase()
        self.get_default_Setting()
        self.set_data()
        self.setup_network_adaptor_screen()

    def get_default_Setting(self):
        data =  self.user_data_base.get_user_settings(self.app.username_input)
        users = self.user_data_base.select_all_users()

        self.logger_.log_info(" ip selected  data  {}".format(json.dumps(data)))
        self.logger_.log_info(" ip selected  users  {}".format(json.dumps(users)))
        if data and len(data) >0 :
            if data[2] ==0:
                self.current_seleected_parameter = data[2]
                self.selected_index =data[2]    
            elif data[2] ==1:
                self.current_seleected_parameter = data[2]
                self.selected_index =data[2]
    



    def set_data(self):
        ip,mask,gate_way= self.system_controller.get_network_info_su_de()
        self.logger_.log_info("==========ip,mask,gate_way {}{}{}".format(ip,mask,gate_way))
        self.ip_address = ip 
        self.sub_mask = mask
        self.gate_Way = gate_way

    def set_up_in_address_field(self):
        # ad ip config 
        ip_screen_height = 15
        ip_screen_width = 50
        popup_y = (self.screen_height - ip_screen_height // 2) // 2
        popup_x = (self.screen_width - ip_screen_width) // 2
        popup_top_height = max(int(0.3 * ip_screen_height), 1)
        popup_bottom_height = ip_screen_height - popup_top_height


        in_win_height = popup_y + popup_top_height +5
        ip_input_x = popup_x + 6


        ip_adrress_label = "IP Address :      [                   ]"
        self.ip_bottom_win.addstr(5, 8, ip_adrress_label, curses.color_pair(3))




        mask_adrress_label = "Subnet Mask :     [                   ]"
        self.ip_bottom_win.addstr(6, 8, mask_adrress_label, curses.color_pair(3))

        getway_label = "Default Getway :  [                   ]"
        self.ip_bottom_win.addstr(7, 8, getway_label, curses.color_pair(3))
         
        self.ip_bottom_win.refresh()
        self.create_update_ip_address()
        curses.curs_set(0)

    def clear_input_fields(self):
        
        if hasattr(self, 'in_address_change') and self.in_address_change !=None:
            self.in_address_change.clear()
            self.in_address_change = None
        if hasattr(self, 'sub_mask_change') and self.sub_mask_change !=None:
            self.sub_mask_change.clear()
            self.sub_mask_change = None 
        if hasattr(self, 'gate_Way_change') and self.gate_Way_change !=None:
            self.gate_Way_change.clear()
            self.gate_Way_change = None 


    def create_update_ip_address(self):
        ip_screen_height = 15
        ip_screen_width = 50
        popup_y = (self.screen_height - ip_screen_height // 2) // 2
        popup_x = (self.screen_width - ip_screen_width) // 2
        self.hostname_screen = curses.newwin(ip_screen_height, ip_screen_width, popup_y, popup_x)

        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = max(int(0.3 * ip_screen_height), 1)
        popup_bottom_height = ip_screen_height - popup_top_height
        
        user_input_y = popup_y + popup_top_height + 5
        user_input_x = popup_x + 30
        self.in_address_change = curses.newwin(1, 16, user_input_y, user_input_x)
        self.in_address_change.bkgd(' ', curses.color_pair(2))
        self.in_address_change.refresh()
    
        self.in_address_change.addstr(0, 0, self.ip_address, curses.color_pair(2))
        self.in_address_change.refresh()
        
        #set mask 
        user_input_y +=1 
        self.sub_mask_change = curses.newwin(1, 16, user_input_y, user_input_x)
        self.sub_mask_change.bkgd(' ', curses.color_pair(2))
        self.sub_mask_change.refresh()
    
        self.sub_mask_change.addstr(0, 0, self.sub_mask, curses.color_pair(2))
        self.sub_mask_change.refresh()

        #gate_Way

        user_input_y +=1 
        self.gate_Way_change = curses.newwin(1, 16, user_input_y, user_input_x)
        self.gate_Way_change.bkgd(' ', curses.color_pair(2))
        self.gate_Way_change.refresh()
    
        self.gate_Way_change.addstr(0, 0, self.gate_Way, curses.color_pair(2))
        self.gate_Way_change.refresh()
        self.set_cursor_position()
        



    
    def setup_network_adaptor_screen(self):
        ip_screen_height = 15
        ip_screen_width = 50
        popup_y = (self.screen_height - ip_screen_height // 2) // 2
        popup_x = (self.screen_width - ip_screen_width) // 2
        self.hostname_screen = curses.newwin(ip_screen_height, ip_screen_width, popup_y, popup_x)

        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = max(int(0.3 * ip_screen_height), 1)
        popup_bottom_height = ip_screen_height - popup_top_height

        # Create windows for each partition within the pop-up window
        self.ip_top_win = self.hostname_screen.subwin(popup_top_height, ip_screen_width, popup_y, popup_x)
        self.ip_bottom_win = self.hostname_screen.subwin(popup_bottom_height, ip_screen_width,
                                                             popup_y + popup_top_height, popup_x)

        # Set background colors for each partition within the pop-up window
        self.ip_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        self.ip_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background

        # Add label to self.ip_top_win

        label_x = (ip_screen_width - len(CONFIGURE_MANAGEMENT_NETWORK_SERVICE)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        self.ip_top_win.addstr(label_y, label_x, CONFIGURE_MANAGEMENT_NETWORK_SERVICE, curses.color_pair(4))

        
         # Add labels to popup_bottom_win
        if not self.current_seleected_parameter:
                
                
                for index, label in enumerate(self.labels):
                    color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                    if self.current_seleected_parameter == index:
                            self.ip_bottom_win.addstr( 2+ index, 2, "[0]",  color_pair)
                            self.ip_bottom_win.addstr( 2+ index, 5, label, color_pair)
                    else:
                        self.ip_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                        self.ip_bottom_win.addstr( 2+ index, 5, label, color_pair)

        else:     
            self.logger_.log_info("sip config selected {}".format(self.current_seleected_parameter))
            for index, label in enumerate(self.labels):
                # color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_seleected_parameter == index and self.starting_state == True:
                    self.starting_state = False
                    self.logger_.log_info("ip config starting_state {}".format(self.current_seleected_parameter)) 
                    color_pair = self.selected_color_pair
                    self.ip_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                    self.ip_bottom_win.addstr( 2+ index, 5, label, color_pair)
                else:
                    self.logger_.log_info("ip config else starting_state {}".format(self.current_seleected_parameter)) 
                    color_pair = self.normal_color_pair
                    self.ip_bottom_win.addstr( 2+ index, 2, "[ ]",color_pair)
                    self.ip_bottom_win.addstr( 2+ index, 5, label, color_pair)

                
            
        
        


         # Add label to popup_bottom_win
        label_text_bottom_esc = "<Space> Selection"
        self.ip_bottom_win.addstr(9, 1, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_esc = "<Esc> Cancel"
        self.ip_bottom_win.addstr(9, 36, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_enter_ok = "<Enter> Ok"
        self.ip_bottom_win.addstr(9, 23, label_text_bottom_enter_ok, curses.color_pair(3))

        
        # Create username input box
        user_input_y = popup_y + popup_top_height + 1
        user_input_x = popup_x + 15        

        self.hostname_screen.refresh()
        if self.current_seleected_parameter ==1:
            self.set_up_in_address_field()
            self.set_cursor_position()
            curses.curs_set(1)
        else:
            self.input_current_index_status = "ip"
            self.clear_input_fields()
            self.set_cursor_position()
            curses.curs_set(0)
    
        

    def set_manually_ip(self):
        self.logger_.log_info("value for self.ip_address,self.sub_mask,self.gate_Way {} {} {}".format(self.ip_address,self.sub_mask,self.gate_Way))
        if len(self.ip_address) >0 and len(self.sub_mask)>0 and len(self.gate_Way) >0 :
            self.system_controller.set_ip_configuration_manual(self.ip_address,self.sub_mask,self.gate_Way)
            self.system_controller.restart_service()

    def set_ip_address_automatic(self):
        self.set_data()
        self.system_controller.reset_ip_config()
        self.system_controller.restart_service()
        
    def clear(self):
        if hasattr(self, 'hostname_screen') and self.hostname_screen != None:
            self.hostname_screen.clear()
            self.hostname_screen.refresh()
            self.hostname_screen = None

    def get_username_input(self):
        return self.current_ssh
    
    def set_cursor_position(self):
        """Set the cursor position based on the current input and status."""
        if   hasattr(self, 'in_address_change') and self.in_address_change !=None and self.input_current_index_status=="ip":
            self.in_address_change.move(0, len(self.ip_address))
            self.in_address_change.refresh()
        
        elif  hasattr(self, 'sub_mask_change') and self.sub_mask_change !=None and self.input_current_index_status=="sub_mask":       
            self.sub_mask_change.move(0, len(self.sub_mask))
            self.sub_mask_change.refresh()

        elif hasattr(self, 'gate_Way_change') and self.gate_Way_change !=None and self.input_current_index_status=="gate_way":
            self.gate_Way_change.move(0, len(self.gate_Way))
            self.gate_Way_change.refresh()
      

    def handle_arrow_key(self, key):
        self.logger_.log_info("==========ip logegr key name {}".format(key.name))
    
        if key.name == "up":
            
            if self.selected_index == 1:
                 self.selected_index = 0
            else:
                 self.selected_index = 0
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_seleected_parameter == index:
                    self.ip_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.ip_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)

                self.ip_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.ip_bottom_win.refresh()
            if self.current_seleected_parameter ==1:
                self.set_up_in_address_field()
                curses.curs_set(1)
            else:
                self.setup_network_adaptor_screen() 
                curses.curs_set(0)

        elif key.name =="down":
            
            if self.selected_index == 0:
                 self.selected_index = 1
            else:
                 self.selected_index = 1
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_seleected_parameter == index:
                    self.ip_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
    
                else:
                    self.ip_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
            
                self.ip_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.ip_bottom_win.refresh()
            if self.current_seleected_parameter ==1:
                self.set_up_in_address_field()
                curses.curs_set(1)
            else:
                self.setup_network_adaptor_screen()
                curses.curs_set(0)

        elif key.name == "space":
            self.current_seleected_parameter = self.selected_index
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if self.current_seleected_parameter == index:
                    self.ip_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                    
                else:
                    self.ip_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
            self.ip_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.ip_bottom_win.refresh()
            if self.current_seleected_parameter ==1:
                        self.set_up_in_address_field()
                        curses.curs_set(1)
            else:
                self.clear_input_fields()
                self.setup_network_adaptor_screen()
                curses.curs_set(0)

        elif key.name == "backspace":
            self.logger_.log_info("=backspace value {}  ={}".format(key.name,self.input_current_index_status))
            if self.input_current_index_status=="ip" and len(self.ip_address)>0:
                self.logger_.log_info("= ip ipipip space key pres key name {}".format(key.name))
                self.ip_address = self.ip_address[:-1]
                self.in_address_change.clear()
                self.in_address_change.bkgd(' ', curses.color_pair(2)) 
                self.in_address_change.addstr(0, 0, self.ip_address, curses.color_pair(2))
                self.in_address_change.refresh()
                self.set_cursor_position()
            
            if self.input_current_index_status=="sub_mask" and len(self.sub_mask)>0:
                self.logger_.log_info("=sub_mask sub_masksub_maskspace key pres key name {}".format(key.name))
                self.sub_mask = self.sub_mask[:-1]
                self.sub_mask_change.clear()
                self.sub_mask_change.bkgd(' ', curses.color_pair(2)) 
                self.sub_mask_change.addstr(0, 0, self.sub_mask, curses.color_pair(2))
                self.sub_mask_change.refresh()
                self.set_cursor_position()

            if self.input_current_index_status=="gate_way" and len(self.gate_Way)>0:
                self.logger_.log_info("=igate_waygate_waygate_wayback space key pres key name {}".format(key.name))
                self.gate_Way = self.gate_Way[:-1]
                self.gate_Way_change.clear()
                self.gate_Way_change.bkgd(' ', curses.color_pair(2)) 
                self.gate_Way_change.addstr(0, 0, self.gate_Way, curses.color_pair(2))
                self.gate_Way_change.refresh()
                self.set_cursor_position()

            
        elif key.name == "tab":
            if self.input_current_index_status=="ip":
                self.input_current_index_status = "sub_mask"
                self.set_cursor_position()
            elif self.input_current_index_status == "sub_mask":
                self.input_current_index_status = "gate_way"
                self.set_cursor_position()

            elif self.input_current_index_status == "gate_way":
                self.input_current_index_status="ip"
                self.set_cursor_position()

        elif len(key.name) == 1:
            self.logger_.log_info("=inside========ip logegr key name {}".format(key.name))
            if   hasattr(self, 'in_address_change') and self.in_address_change !=None and self.input_current_index_status=="ip" and len(self.ip_address)<15:
                self.ip_address +=key.name
                self.in_address_change.addstr(0, 0, self.ip_address, curses.color_pair(2))
                self.in_address_change.refresh()
                self.set_cursor_position()
            
            elif  hasattr(self, 'sub_mask_change') and self.sub_mask_change !=None and self.input_current_index_status=="sub_mask" and len(self.sub_mask)<15:
                self.sub_mask +=key.name
                self.sub_mask_change.addstr(0, 0, self.sub_mask, curses.color_pair(2))
                self.sub_mask_change.refresh()
                self.set_cursor_position()

            elif hasattr(self, 'gate_Way_change') and self.gate_Way_change !=None and self.input_current_index_status=="gate_way" and len(self.gate_Way)<15:
                self.gate_Way +=key.name
                self.gate_Way_change.addstr(0, 0, self.gate_Way, curses.color_pair(2))
                self.gate_Way_change.refresh()
                self.set_cursor_position()

            


            
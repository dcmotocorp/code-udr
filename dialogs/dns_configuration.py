import curses
from logs.udr_logger import UdrLogger
from dialogs.system_config import SystemConfig
from constant import KEY_UP,KEY_DOWN,CONFIGURE_MANAGEMENT_NETWORK_SERVICE,OBTAIN_IP_AUTOMATIC,MANUALLY_IP_AUTOMATIC,MANUALLY_DNS_AUTOMATIC,OBTAIN_DNS_AUTOMATIC
from system_controller.systemcontroler import SystemControler
import warnings
from data.database import UserDatabase

warnings.filterwarnings("ignore")
class DNSScreen:
    def __init__(self, screen_height, screen_width,app):
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.current_ssh = ""
        self.autheticated_parameter = True
        self.update_status = False
        self.current_seleected_parameter = None
        self.current_selected_label_index = None
        self.labels = [OBTAIN_DNS_AUTOMATIC, MANUALLY_DNS_AUTOMATIC]
        self.normal_color_pair = curses.color_pair(3) 
        self.selected_color_pair = curses.color_pair(5)
        self.logger_ = UdrLogger()
        self.selected_index= 0
        self.user_data_base = UserDatabase()
        self.system_controller = SystemControler()
        self.primary = "192.168.1.1"
        self.starting_state =True
        self.secondary =  "192.168.1.1"
        self.input_current_index_status = "prim"
        self.get_dns_priomary_secondary()
        self.get_default_Setting()
        self.setup_network_adaptor_screen()

    
    def get_default_Setting(self):
        data =  self.user_data_base.get_user_settings(self.app.username_input)
        users = self.user_data_base.select_all_users()

        if data and len(data) >0 :
            if data[3] ==0:
                self.current_selected_label_index = data[3]    
            elif data[3] ==1:
                self.current_selected_label_index = data[3]

    
    def create_update_dns_address(self):
        ip_screen_height = 15
        ip_screen_width = 50
        popup_y = (self.screen_height - ip_screen_height // 2) // 2
        popup_x = (self.screen_width - ip_screen_width) // 2
        
        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = max(int(0.3 * ip_screen_height), 1)
        popup_bottom_height = ip_screen_height - popup_top_height
        
        user_input_y = popup_y + popup_top_height + 5
        user_input_x = popup_x + 34
        self.primary_change = curses.newwin(1, 14, user_input_y, user_input_x)
        self.primary_change.bkgd(' ', curses.color_pair(2))
        self.primary_change.refresh()
    
        self.primary_change.addstr(0, 0, self.primary, curses.color_pair(2))
        self.primary_change.refresh()
        
        #set mask 
        user_input_y +=1 
        self.secondary_change = curses.newwin(1, 14, user_input_y, user_input_x)
        self.secondary_change.bkgd(' ', curses.color_pair(2))
        self.secondary_change.refresh()
    
        self.secondary_change.addstr(0, 0, self.secondary, curses.color_pair(2))
        self.secondary_change.refresh()

        
    def clear_input_fields(self):
        
        if hasattr(self, 'primary_change') and self.primary_change !=None:
            self.primary_change.clear()
            self.primary_change = None
        if hasattr(self, 'secondary_change') and self.secondary_change !=None:
            self.secondary_change.clear()
            self.secondary_change = None 
           
    
    def get_dns_priomary_secondary(self):
        primary,secondary = self.system_controller.get_dns_configuration_linux()
        self.primary =primary
        self.secondary = secondary
    
    def set_auto_dns(self):
        self.get_dns_priomary_secondary()
        self.system_controller.set_dns_auto_assign()
    
    def set_manually_dns(self):
        self.system_controller.set_dns_servers(self.primary,self.secondary)

    def set_up_in_address_field(self):
        # ad ip config 
        ip_adrress_label = "Primary DNS Server :   [                ]"
        self.auth_bottom_win.addstr(5, 8, ip_adrress_label, curses.color_pair(3))
        mask_adrress_label = "Secondary DNS Server : [                ]"
        self.auth_bottom_win.addstr(6, 8, mask_adrress_label, curses.color_pair(3))
        self.auth_bottom_win.refresh()
        self.create_update_dns_address()
    
    
        
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
            if index == self.current_selected_label_index:
                if self.starting_state == True:
                    self.starting_state = False
                    color_pair = self.selected_color_pair
                self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
            else:
                self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
            self.auth_bottom_win.addstr( 2+ index, 5, label, color_pair)
     

        # Add label to popup_bottom_win
        label_text_bottom_esc = "<Space> Selection"
        self.auth_bottom_win.addstr(9, 1, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_esc = "<Esc> Cancel"
        self.auth_bottom_win.addstr(9, 36, label_text_bottom_esc, curses.color_pair(3))

        label_text_bottom_enter_ok = "<Enter> Ok"
        self.auth_bottom_win.addstr(9, 23, label_text_bottom_enter_ok, curses.color_pair(3))
        

        auth_top_win.refresh()
        self.auth_bottom_win.refresh()
        curses.curs_set(1)
        self.hostname_screen.refresh()
        # if self.current_selected_label_index ==1:
        #     self.set_up_in_address_field()
        #     self.set_cursor_position()
        # else:
        #     self.clear_input_fields()
        
        if self.current_selected_label_index ==1:
            self.set_up_in_address_field()
            self.set_cursor_position()
        else:
            self.input_current_index_status = "prim"
            self.clear_input_fields()
            self.set_cursor_position()
    def clear(self):
        if hasattr(self, 'hostname_screen') and self.hostname_screen != None:
            self.hostname_screen.clear()
            self.hostname_screen.refresh()
            self.hostname_screen = None

    def get_username_input(self):
        return self.current_ssh
    
    def handle_arrow_key(self, key):
        if key.name== "up":
            if self.selected_index == 1:
                 self.selected_index = 0
            else:
                 self.selected_index = 0
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if index == self.current_selected_label_index:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                self.auth_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.auth_bottom_win.refresh()
            if self.current_selected_label_index ==1:
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
                if index == self.current_selected_label_index:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                self.auth_bottom_win.addstr(2 + index, 5, label, color_pair)
            self.auth_bottom_win.refresh()
            if self.current_selected_label_index ==1:
                self.set_up_in_address_field()
            else:
                self.setup_network_adaptor_screen()
    
        
        
        elif key.name == "space":
            self.current_selected_label_index = self.selected_index
            for index, label in enumerate(self.labels):
                color_pair = self.selected_color_pair if index == self.selected_index else self.normal_color_pair
                if index == self.current_selected_label_index:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[0]", color_pair)
                else:
                    self.auth_bottom_win.addstr( 2+ index, 2, "[ ]", color_pair)
                self.auth_bottom_win.addstr(2 + index, 5, label, color_pair)
            
            if self.current_selected_label_index ==1:
                self.set_up_in_address_field()
            else:
                self.setup_network_adaptor_screen() 
        elif key.name == "tab":
            if self.input_current_index_status=="prim":
                self.input_current_index_status="seco"
                self.set_cursor_position()
            elif self.input_current_index_status=="seco":
                self.input_current_index_status="prim"
                self.set_cursor_position()
        elif key.name == "backspace":
            if self.input_current_index_status=="prim" and len(self.primary)>0:
                self.primary = self.primary[:-1]
                self.primary_change.clear()
                self.primary_change.bkgd(' ', curses.color_pair(2)) 
                self.primary_change.addstr(0, 0, self.primary, curses.color_pair(2))
                self.primary_change.refresh()
                self.set_cursor_position()
            
            if self.input_current_index_status=="seco" and len(self.secondary)>0:
                self.secondary = self.secondary[:-1]
                self.secondary_change.clear()
                self.secondary_change.bkgd(' ', curses.color_pair(2)) 
                self.secondary_change.addstr(0, 0, self.secondary, curses.color_pair(2))
                self.secondary_change.refresh()
                self.set_cursor_position()
        
        elif len(key.name) == 1:
            self.logger_.log_info("=inside========ip logegr key name {}".format(key.name))
            if   hasattr(self, 'primary_change') and self.primary_change !=None and self.input_current_index_status=="prim" and len(self.primary)<13:
                self.primary +=key.name
                self.primary_change.addstr(0, 0, self.primary, curses.color_pair(2))
                self.primary_change.refresh()
                self.set_cursor_position()
            
            elif  hasattr(self, 'secondary_change') and self.secondary_change !=None and self.input_current_index_status=="seco" and len(self.secondary)<13:
                self.secondary +=key.name
                self.secondary_change.addstr(0, 0, self.secondary, curses.color_pair(2))
                self.secondary_change.refresh()
                self.set_cursor_position()

    def set_cursor_position(self):
        """Set the cursor position based on the current input and status."""
        if  hasattr(self, 'primary_change') and self.primary_change !=None and self.input_current_index_status=="prim":
            self.primary_change.move(0, len(self.primary))
            self.primary_change.refresh()
        
        elif  hasattr(self, 'secondary_change') and self.secondary_change !=None and self.input_current_index_status=="seco":       
            self.secondary_change.move(0, len(self.secondary))
            self.secondary_change.refresh()


            

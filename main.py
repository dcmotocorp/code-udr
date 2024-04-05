import curses
from utils import shutdown_computer, get_ip_address, restart_computer

class NovaiguApplication:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.popup_win = None
        
        self.setup_windows()

    def setup_windows(self):
        # Initialize curses
        curses.start_color()
        curses.use_default_colors()

        # Set up color pairs
        curses.init_pair(1, curses.COLOR_BLACK,242)  # Grey background
        curses.init_pair(2, curses.COLOR_BLACK, 130)  # Orange background
        curses.init_pair(3,curses.COLOR_WHITE,130)
        curses.init_pair(4,curses.COLOR_WHITE,242)
        

        # Get screen dimensions
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()

        # Calculate dimensions for the two partitions
        top_height = int(0.6 * self.screen_height)
        bottom_height = self.screen_height - top_height

        # Create windows for each partition
        self.top_win = curses.newwin(top_height, self.screen_width, 0, 0)
        self.bottom_win = curses.newwin(bottom_height, self.screen_width, top_height, 0)

        # Set background colors for each partition
        self.top_win.bkgd(' ', curses.color_pair(1))  # Grey background
        self.bottom_win.bkgd(' ', curses.color_pair(2))  # Orange background

        # Draw borders to distinguish the partitions
        self.stdscr.hline(top_height, 0, '-', self.screen_width)
        self.stdscr.refresh()

        # Refresh the windows to apply changes
        self.top_win.refresh()
        self.bottom_win.refresh()

        # Define labels
        novaigu_label = "Novaigu Udr 1.0.0"
        novaigu_platform_label = "Novaigu Inc Platform"
        ip_address = get_ip_address()
        novaigu_http_label = "Https://{}".format(ip_address)

        # Calculate positions for labels
        label_width = max(len(novaigu_label), len(novaigu_platform_label), len(novaigu_http_label))
        label_height = 2
        label_x = (self.screen_width - label_width) // 2
        label_y = top_height // 2

        # Add labels to self.top_win
        self.top_win.addstr(label_y, label_x, novaigu_label)
        self.top_win.addstr(label_y + label_height, label_x, novaigu_platform_label)
        self.top_win.addstr(label_y + 2 * label_height, label_x, novaigu_http_label)

        # Refresh the self.top_win to apply changes
        self.top_win.refresh()

        # Add clickable label at the bottom-left corner
        self.bottom_win.addstr(bottom_height - 2, 1, "<F2> Configuration System", curses.A_UNDERLINE)
        self.bottom_win.addstr(bottom_height - 2, self.screen_width-len("<F12> Shut down/Restart")-2, "<F12> Shut down/Restart", curses.A_UNDERLINE)
        self.bottom_win.refresh()

    
    def create_shut_down_restart_pop_up(self):
        self.top_win.bkgd(' ', curses.color_pair(0))  # Black background
        self.bottom_win.bkgd(' ', curses.color_pair(0))
        self.top_win.refresh()
        self.bottom_win.refresh()
        # Create a pop-up window
        popup_height = 10
        popup_width = 40
        popup_y = (self.screen_height - popup_height//2) // 2
        popup_x = (self.screen_width - popup_width) // 2
        self.popup_win = curses.newwin(popup_height, popup_width, popup_y, popup_x)

        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = int(0.3 * popup_height)
        popup_bottom_height = popup_height - popup_top_height

        # Create windows for each partition within the pop-up window
        popup_top_win = self.popup_win.subwin(popup_top_height, popup_width, popup_y, popup_x)
        popup_bottom_win = self.popup_win.subwin(popup_bottom_height, popup_width, popup_y + popup_top_height, popup_x)

        # Set background colors for each partition within the pop-up window
        popup_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        popup_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background


        # Add label to popup_top_win
        label_text = "Shut Down/Restart"
        label_x = (popup_width - len(label_text)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        popup_top_win.addstr(label_y, label_x, label_text)

        # Add label to popup_bottom_win
        label_text_bottom = "<F2> Shut down"
        label_x_bottom = 3
        label_y_bottom =1 # Center vertically
        popup_bottom_win.addstr(label_y_bottom, label_x_bottom, label_text_bottom)

        # Add label to popup_bottom_win
        label_text_bottom_12 = "<F11> Restart"
        label_x_bottom = 3
        label_y_bottom =3 # Center vertically
        popup_bottom_win.addstr(label_y_bottom, label_x_bottom, label_text_bottom_12)

        # Add label to popup_bottom_win
        label_text_bottom_esc = "<Esc> Cancle"
        label_x_bottom = 25
        label_y_bottom =5 # Center vertically
        popup_bottom_win.addstr(label_y_bottom, label_x_bottom, label_text_bottom_esc)
        self.popup_win.refresh()


    def authentication_screen(self):
        self.top_win.bkgd(' ', curses.color_pair(0))  # Black background
        self.bottom_win.bkgd(' ', curses.color_pair(0))
        self.top_win.refresh()
        self.bottom_win.refresh()
        
        # Create a pop-up window
        auth_screen_height = 10
        auth_screen_width = 40
        popup_y = (self.screen_height - auth_screen_height//2) // 2
        popup_x = (self.screen_width - auth_screen_width) // 2
        self.authentication_screen = curses.newwin(auth_screen_height, auth_screen_width, popup_y, popup_x)

        # Calculate dimensions for the two partitions within the pop-up window
        popup_top_height = max(int(0.3 * auth_screen_height), 1)
        popup_bottom_height = auth_screen_height - popup_top_height

        # Create windows for each partition within the pop-up window
        auth_top_win = self.authentication_screen.subwin(popup_top_height, auth_screen_width, popup_y, popup_x)
        auth_bottom_win = self.authentication_screen.subwin(popup_bottom_height, auth_screen_width, popup_y + popup_top_height, popup_x)

        # Set background colors for each partition within the pop-up window
        auth_top_win.bkgd(' ', curses.color_pair(1))  # Yellow background
        auth_bottom_win.bkgd(' ', curses.color_pair(2))  # Grey background

        # Add label to auth_top_win
        label_text = "Authentication"
        label_x = (auth_screen_width - len(label_text)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        auth_top_win.addstr(label_y, label_x, label_text,curses.color_pair(4))


        username_label = "Username:  ["
        auth_bottom_win.addstr(1, 1, username_label,curses.color_pair(3))

        end_bracket_user = "]"
        auth_bottom_win.addstr(1, 35, end_bracket_user,curses.color_pair(3))

        # Add label to popup_bottom_win
        label_text_bottom_esc = "<Esc> Cancle"

        auth_bottom_win.addstr(5, 25, label_text_bottom_esc,curses.color_pair(3))

        label_text_bottom_enter_ok = "<Enter> Ok"

        auth_bottom_win.addstr(5, 11, label_text_bottom_enter_ok,curses.color_pair(3))
   


        # Create username input box
        user_input_y = popup_y +popup_top_height+1
        user_input_x = popup_x +13
        username_win = curses.newwin(1, 20, user_input_y, user_input_x)
        username_win.refresh()
        username_input = ""


        # Print password label
        password_label = "Password:  ["
        auth_bottom_win.addstr(3, 1, password_label, curses.color_pair(3))
        
        auth_bottom_win.addstr(3, 35, end_bracket_user,curses.color_pair(3))
        # Create password input box\
        password_input_y= user_input_y+2
        password_win = curses.newwin(2, 20, password_input_y, user_input_x)
        password_win.refresh()
        password_input = ""



        # Set placeholders for username and password fields
        username_placeholder = "Enter username"
        password_placeholder = "Enter password"
        username_win.addstr(0, 0, username_placeholder, curses.color_pair(3))
        password_win.addstr(0, 0, password_placeholder, curses.color_pair(3))
        username_win.refresh()
        password_win.refresh()

        
        curses.curs_set(1)
        self.authentication_screen.refresh()
        
       
        while True:
            if len(username_input) <15:
                username_win.addstr(0, 0, username_input, curses.color_pair(1))
            username_win.refresh()
            ch = username_win.getch()
            
            if ch == 27:
                if self.authentication_screen:
                    self.authentication_screen.clear()
                    self.authentication_screen.refresh()
                    self.authentication_screen = None
                self.top_win.bkgd(' ', curses.color_pair(1))  # Grey background
                self.bottom_win.bkgd(' ', curses.color_pair(2))  # Orange background
                self.top_win.refresh()
                self.bottom_win.refresh()
            
            if ch == curses.KEY_ENTER or ch == 10:
                if len(username_input) == 0:
                    continue  # Don't proceed if username is empty
                break 
            elif ch == curses.KEY_BACKSPACE or ch == 8:
                username_input = username_input[:-1]
            else:
                username_input += chr(ch)
            # Get password input
        while True:
            if len(password_input) <15:
                username_win.addstr(0, 0, password_input, curses.color_pair(1))
            password_win.addstr(0, 0, "*" * len(password_input), curses.color_pair(1))
            password_win.refresh()
            ch = password_win.getch()
            
            if ch == 27:
                if self.authentication_screen:
                    username_win.clear()
                    password_win.clear()
                    username_win.refresh()
                    username_win = None

                    password_win.refresh()
                    password_win = None

                    self.authentication_screen.clear()
                    self.authentication_screen.refresh()
                    self.authentication_screen = None
                self.top_win.bkgd(' ', curses.color_pair(1))  # Grey background
                self.bottom_win.bkgd(' ', curses.color_pair(2))  # Orange background
                self.top_win.refresh()
                self.bottom_win.refresh()


            if ch == curses.KEY_ENTER or ch == 10:
                if len(password_input) == 0:
                    continue  # Don't proceed if username is empty
                
                else:
                    self.authentication_screen.clear()
                    self.authentication_screen.refresh()
                    self.authentication_screen = None

                    
                    self.top_win.bkgd(' ', curses.color_pair(1))  # Grey background
                    self.bottom_win.bkgd(' ', curses.color_pair(2))  # Orange background
                    self.top_win.refresh()
                    self.bottom_win.refresh()
                    
                    break
                
 
            elif ch == curses.KEY_BACKSPACE or ch == 127:
                password_input = password_input[:-1]
            else:
                password_input += chr(ch)
        
        # Clear input boxes
        username_win.clear()
        password_win.clear()
        username_win.refresh()
        password_win.refresh()
        
        # Disable cursor
        curses.curs_set(0)


         


        


    def run(self):
        while True:
            key = self.stdscr.getch()   
            if key == curses.KEY_F2:
                if self.popup_win:
                    shutdown_computer() 
                else:
                    if self.authentication_screen:
                        
                        self.authentication_screen()
                        self.authentication_screen = None
            
            if key == curses.KEY_ENTER or key == 10:
                self.top_win.bkgd(' ', curses.color_pair(1))  # Grey background
                self.bottom_win.bkgd(' ', curses.color_pair(2))  # Orange background
                self.top_win.refresh()
                self.bottom_win.refresh()
 

            if key == 287:
                if self.popup_win:
                    restart_computer()
            elif key == curses.KEY_F12:
                    self.create_shut_down_restart_pop_up()
            elif key == 27:
                if self.popup_win:
                    self.popup_win.clear()  # KEY_ESC the pop-up window
                    self.popup_win.refresh()
                    self.popup_win = None 
                if self.authentication_screen:
                    self.authentication_screen.clear()
                    self.authentication_screen.refresh()
                    self.authentication_screen = None
                self.top_win.bkgd(' ', curses.color_pair(1))  # Grey background
                self.bottom_win.bkgd(' ', curses.color_pair(2))  # Orange background
                self.top_win.refresh()
                self.bottom_win.refresh()


def main(stdscr):
    app= NovaiguApplication(stdscr)
    app.run()


curses.wrapper(main)





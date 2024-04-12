import curses
from constant import SHUT_DOWN_RESTART, F2_SHUT_DOWN, F11_RESTART, ESC_CANCLE,KEY_ESC


class ShutdownRestart:
    def __init__(self, screen_height, screen_width,app=None):
        self.popup_win = None
        self.app = app
        self.screen_height = screen_height
        self.screen_width = screen_width
       
    

    def create_shut_down_restart_pop_up(self, stdscr):
        # Create a pop-up window    
        popup_height = 10
        popup_width = 40
        popup_y = (self.screen_height - popup_height // 2) // 2
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
        label_x = (popup_width - len(SHUT_DOWN_RESTART)) // 2
        label_y = (popup_top_height - 1) // 2  # Center vertically
        popup_top_win.addstr(label_y, label_x, SHUT_DOWN_RESTART)

        # Add label to popup_bottom_win
        label_x_bottom = 3
        label_y_bottom = 1  # Center vertically
        popup_bottom_win.addstr(label_y_bottom, label_x_bottom, F2_SHUT_DOWN)

        # Add label to popup_bottom_win
        label_x_bottom = 3
        label_y_bottom = 3  # Center vertically
        popup_bottom_win.addstr(label_y_bottom, label_x_bottom, F11_RESTART)

        # Add label to popup_bottom_win
        label_x_bottom = 25
        label_y_bottom = 5  # Center vertically
        popup_bottom_win.addstr(label_y_bottom, label_x_bottom, ESC_CANCLE)
        self.popup_win.refresh()
        curses.curs_set(1)

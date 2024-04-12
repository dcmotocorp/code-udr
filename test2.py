import curses

def authentication_screen(stdscr):
    # Clear the screen
    stdscr.clear()

    # Define the prompt text
    prompt_text = "Username:"

    # Define the coordinates for the prompt text
    prompt_y = 5  # Y coordinate
    prompt_x = 5  # X coordinate

    # Display the prompt text
    stdscr.addstr(prompt_y, prompt_x, prompt_text)

    # Define the coordinates for the input field (right after the prompt)
    input_y = prompt_y
    input_x = prompt_x + len(prompt_text) + 1

    # Initialize the input field with an empty string
    username = []

    # Define a variable to keep track of the cursor position
    cursor_position = 0

    # Enable keypad input
    stdscr.keypad(True)

    # Turn off automatic echoing of keystrokes
    curses.noecho()

    # Turn on instant key response (no waiting for Enter)
    curses.cbreak()

    
    while True:
        pass 

if __name__ == "__main__":
    curses.wrapper(authentication_screen)

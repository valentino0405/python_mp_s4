# main.py
from gui import create_gui
from voice_commands import start_voice_assistant, listen

def main():
    # Create the root window and GUI
    root, components = create_gui(start_voice_assistant, listen)

    # Set up the main event loop
    if __name__ == "__main__":
        root.mainloop()

if __name__ == "__main__":
    main()
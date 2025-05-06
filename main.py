import dearpygui.dearpygui as dpg
import sys
import os
from pathlib import Path

# Add the current directory to PATH to ensure all modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all required modules
from home import homeui
from hostlookup import hostlookupgui
from portscanner import portscanner
from webdir import webdirscanner
from themes import create_themes
from fontsetup import setUp

def main():
    # Initialize DearPyGui
    dpg.create_context()
    dpg.create_viewport(title='Network Security Scanner', width=800, height=600)
    dpg.setup_dearpygui()
    
    # Set the viewport background color
    dpg.set_viewport_clear_color((0, 0, 0, 255))
    
    # Create themes for the UI
    create_themes()
    
    # Initialize the font
    setUp()
    
    # Start with the home UI
    homeui()
    
    # Show the viewport and start the main loop
    dpg.show_viewport()
    dpg.start_dearpygui()
    
    # Clean up when application exits
    dpg.destroy_context()

if __name__ == "__main__":
    main()

import dearpygui.dearpygui as dpg
import threading
import tkinter as tk
from tkinter import filedialog
from fontsetup import setUp
from themes import create_themes
from code import find_subdirectories
from resize import homeResize
import time

class StopScaning:
    def __init__(self):
        self.scan = True

def resize():
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("main_window", width)
    dpg.set_item_height("main_window", height)

    dpg.set_item_pos("ip_text", [(width / 2) - 150, (height / 2) - 140])
    dpg.set_item_pos("input", [(width / 2) - 10, (height / 2) - 140])
    dpg.set_item_pos("ws_text", [(width / 2) - 150, (height / 2) - 80])
    dpg.set_item_pos("input_ws", [(width / 2) - 10, (height / 2) - 80])
    dpg.set_item_pos("browse_button_ws", [(width / 2) + 200, (height / 2) - 80])
    dpg.set_item_pos("scan_button_ws", [(width / 2) - 10, (height / 2) - 30])
    dpg.set_item_pos("back_button_ws", [width - 120, 10])
    dpg.set_item_pos("result_text", [(width / 2) - 390, (height / 2) + 50])

def return_to_home(sender,app_data,user_data):
    user_data.scan = False
    dpg.hide_item("main_window")
    dpg.show_item("main_window_home")
    homeResize()
    dpg.set_viewport_resize_callback(lambda: homeResize())

def browse_wordlist():
    # We need to create a root Tk window for the file dialog, but hide it
    root = tk.Tk()
    root.withdraw()
    
    # Open the file dialog
    file_path = filedialog.askopenfilename(
        title="Select Wordlist File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    # Update the input field with the selected file path
    if file_path:
        dpg.set_value("input_ws", file_path)
    
    # Destroy the Tk window
    root.destroy()

def run_scan(sender,app_data,user_data):
    user_data.scan = False
    url = dpg.get_value("input")
    wordlist_file = dpg.get_value("input_ws")
    
    if not url:
        dpg.set_value("result_text", "Please enter a URL to scan.")
        return
    
    if not wordlist_file:
        dpg.set_value("result_text", "Please select a wordlist file.")
        return
    
    dpg.set_value("result_text", "Starting web directory scan...")
    
    # Run the scan in a separate thread to avoid freezing the UI
    def scan_thread(stopInstance):
        def update_callback(result):
            dpg.set_value("result_text", result)
        
        find_subdirectories(url, wordlist_file, update_callback ,stopInstance)
    time.sleep(2)
    user_data.scan = True
    threading.Thread(target=scan_thread,args=(user_data,), daemon=True).start()

def webdirscanner():
    # Delete existing window if it exists 
    if dpg.does_item_exist("main_window"):
        dpg.delete_item("main_window")
    stop = StopScaning()
    with dpg.window(tag="main_window", label="Web Sub-directory Scanner", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
        dpg.add_text("Web Sub-directory Scanner", tag="wss", color=(255, 255, 255, 255))
        dpg.add_separator(tag="separator")
        dpg.add_text("Enter The URL Here:", tag="ip_text", color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input", height=30, width=200, hint="e.g. https://example.com")
        dpg.add_text("Select Wordlist:", tag='ws_text', color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input_ws", readonly=True, default_value="", height=30, width=200)
        dpg.add_button(label="Scan", tag="scan_button_ws", pos=(0, 0), width=100, height=30, callback=run_scan,user_data=stop)
        dpg.add_button(label="Browse", tag="browse_button_ws", pos=(0, 0), width=100, height=30, callback=browse_wordlist)
        dpg.add_button(label="Back", tag="back_button_ws", pos=(0, 0), width=100, height=30, callback=return_to_home,user_data=stop)
        dpg.add_input_text(tag="result_text", multiline=True, readonly=True, default_value="", width=700, height=200)

        # Create themes
        create_themes()

        # Bind themes
        dpg.bind_item_theme("scan_button_ws", "button_theme")
        dpg.bind_item_theme("input", "input_theme")
        dpg.bind_item_theme("input_ws", "input_theme")
        dpg.bind_item_theme("browse_button_ws", "button_theme")
        dpg.bind_item_theme("back_button_ws", "button_theme")
        dpg.bind_item_theme("result_text", "input_theme_result")
        dpg.bind_item_font("wss", setUp())

    # Call resize after the window is created
    resize()
    dpg.set_viewport_resize_callback(lambda: resize())
    dpg.hide_item("main_window_home")

if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title='Web Sub-directory Scanner', width=800, height=600)
    dpg.setup_dearpygui()

    # Import here to avoid circular imports
    from home import homeui
    homeui()
    webdirscanner()

    # Set the global background color to match the theme
    dpg.set_viewport_clear_color((0, 0, 0, 255))

    dpg.show_viewport()
    dpg.start_dearpygui()

    dpg.destroy_context()

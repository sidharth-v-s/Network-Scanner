import dearpygui.dearpygui as dpg
import nmap
import requests
import os
import threading
import concurrent.futures
import tkinter as tk
from tkinter import filedialog
from fontsetup import setUp

# Function to find subdirectories on a web server
def find_subdirectories(url, wordlist_file, callback=None):
    results = []
    
    # Ensure the URL format ends with a '/'
    if not url.endswith('/'):
        url += '/'
    
    # Read the wordlist file with the appropriate encoding
    try:
        with open(wordlist_file, 'r', encoding='ISO-8859-1') as file:
            subdirs = file.read().splitlines()
    except FileNotFoundError:
        results.append(f"Error: The file '{wordlist_file}' was not found.")
        if callback:
            callback("\n".join(results))
        return
    except UnicodeDecodeError:
        # Try with UTF-8 if ISO-8859-1 fails
        try:
            with open(wordlist_file, 'r', encoding='utf-8') as file:
                subdirs = file.read().splitlines()
        except UnicodeDecodeError:
            results.append(f"Error: The file '{wordlist_file}' contains invalid characters.")
            if callback:
                callback("\n".join(results))
            return

    results.append(f"Starting directory scan on: {url}\n")
    if callback:
        callback("\n".join(results))

    # Check each subdirectory in the wordlist
    found_count = 0
    for subdir in subdirs:
        if not subdir.strip():  # Skip empty lines
            continue
            
        full_url = f"{url}{subdir}"
        try:
            response = requests.get(full_url, timeout=5)
            # If response code is 200, directory likely exists
            if response.status_code == 200:
                found_count += 1
                results.append(f"Found: {full_url}")
                if callback and found_count % 5 == 0:  # Update UI every 5 findings
                    callback("\n".join(results))
        except requests.RequestException as e:
            results.append(f"Error reaching {full_url}: {e}")
            if callback and found_count % 5 == 0:
                callback("\n".join(results))
    
    results.append(f"\nScan complete. Found {found_count} directories.")
    if callback:
        callback("\n".join(results))
    return results

# Host Lookup Function
def nmap_scan(subnet, callback=None):
    results = []
    results.append(f"Starting host lookup on subnet: {subnet}")
    if callback:
        callback("\n".join(results))
        
    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=subnet, arguments='-sn')
        up_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']
        
        if up_hosts:
            results.append("Hosts found:")
            for host in up_hosts:
                results.append(host)
        else:
            results.append("No hosts found.")
    except Exception as e:
        results.append(f"Error during host lookup: {str(e)}")
    
    if callback:
        callback("\n".join(results))
    return results

# Port Scanner Function
def port_scanner(port_ip, callback=None):
    results = []
    results.append(f"Starting port scan on IP: {port_ip}")
    if callback:
        callback("\n".join(results))
        
    try:
        np = nmap.PortScanner()
        np.scan(port_ip, arguments='-sV -p 80,20,21,22,23,25,53,110,443,66,8000 -T4')
        
        for proto in np[port_ip].all_protocols():
            lport = np[port_ip][proto].keys()
            for port in lport:
                if np[port_ip][proto][port]['state'] == 'open':
                    service = np[port_ip][proto][port]['name']
                    version = np[port_ip][proto][port].get('version', 'unknown')
                    results.append(f"Port {port} is open, Service: {service}, Version: {version}")
        
        # Try to get OS info if available
        try:
            if 'osmatch' in np[port_ip] and np[port_ip]['osmatch']:
                os_info = np[port_ip]['osmatch'][0]['name']
                results.append(f"OS: {os_info}")
        except:
            pass
            
        if len(results) == 1:  # Only the starting message
            results.append("No open ports found.")
            
    except Exception as e:
        results.append(f"Error during port scan: {str(e)}")
    
    if callback:
        callback("\n".join(results))
    return results

# HOME UI
def resize():
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("main_window_home", width)
    dpg.set_item_height("main_window_home", height)
    dpg.set_item_pos("exit_button", [width - 120, 10])
    dpg.set_item_pos("hlu_button_home", [(width / 2) - 95, (height / 2) - 150])
    dpg.set_item_pos("ps_button_home", [(width / 2) - 95, (height / 2) - 75])
    dpg.set_item_pos("sdf_button_home", [(width / 2) - 95, (height / 2) - 0])

def home_ui():
    if dpg.does_item_exist("main_window_home"):
        dpg.show_item("main_window_home")
    else:
        with dpg.window(tag="main_window_home", label="INFO GATHER", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
            dpg.add_text("Network Security Scanner", tag="mh", color=(255, 255, 255, 255))
            dpg.add_separator()

            # Get the current viewport size
            width = dpg.get_viewport_width()
            height = dpg.get_viewport_height()

            dpg.add_button(label="Host Look Up", tag="hlu_button_home", pos=(0, 0), width=190, height=40, callback=host_lookup_gui)
            dpg.add_button(label="Port Scanner", tag="ps_button_home", pos=(0, 50), width=190, height=40, callback=port_scanner_gui)
            dpg.add_button(label="Web Subdirectory Finder", tag="sdf_button_home", pos=(0, 100), width=190, height=40, callback=webdir_scanner_gui)
            dpg.add_button(label="Exit", tag="exit_button", pos=(width - 120, 10), width=100, height=30, callback=lambda: dpg.stop_dearpygui())

            create_themes()
            
            dpg.bind_item_theme("hlu_button_home", "button_theme")
            dpg.bind_item_theme("ps_button_home", "button_theme")
            dpg.bind_item_theme("sdf_button_home", "button_theme")
            dpg.bind_item_theme("exit_button", "button_theme")
            dpg.bind_item_font("mh", setUp())

            dpg.set_frame_callback(1, resize)
            dpg.set_viewport_resize_callback(lambda: resize())

        resize()  # Call once to initialize the sizes

# HOST LOOKUP GUI
def host_lookup_gui():
    create_themes()

    if dpg.does_item_exist("main_window"):
        dpg.delete_item("main_window")

    with dpg.window(tag="main_window", label="Host Look Up", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
        dpg.add_text("Host Look Up Tool", tag="hlup", color=(255, 255, 255, 255))
        dpg.add_separator(tag="separator")
        dpg.add_text("Enter The Subnet Here:", tag="ip_text", color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input", height=30, width=200, hint="e.g. 192.168.1.0/24")
        dpg.add_button(label="Scan", tag="scan_button_hlu", pos=(0, 0), width=100, height=30, callback=run_host_lookup)
        dpg.add_button(label="Back", tag="back_button_hlu", pos=(0, 0), width=100, height=30, callback=return_to_home)
        dpg.add_input_text(tag="result_text", multiline=True, readonly=True, default_value="", width=700, height=200)

        # Bind Themes
        dpg.bind_item_theme("scan_button_hlu", "button_theme")
        dpg.bind_item_theme("input", "input_theme")
        dpg.bind_item_theme("back_button_hlu", "button_theme")
        dpg.bind_item_theme("result_text", "input_theme_result")
        dpg.bind_item_font("hlup", setUp())

    host_lookup_resize()
    dpg.set_viewport_resize_callback(lambda: host_lookup_resize())
    dpg.hide_item("main_window_home")

def host_lookup_resize():
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("main_window", width)
    dpg.set_item_height("main_window", height)

    dpg.set_item_pos("ip_text", [(width / 2) - 190, (height / 2) - 40])
    dpg.set_item_pos("input", [(width / 2) - 10, (height / 2) - 40])
    dpg.set_item_pos("scan_button_hlu", [(width / 2) - 10, (height / 2) + 10])
    dpg.set_item_pos("back_button_hlu", [width - 120, 10])
    dpg.set_item_pos("result_text", [(width / 2) - 350, (height / 2) + 120])

def run_host_lookup():
    subnet = dpg.get_value("input")
    if not subnet:
        dpg.set_value("result_text", "Please enter a subnet to scan.")
        return
        
    dpg.set_value("result_text", "Starting host lookup...")
    
    # Run nmap scan in a separate thread to avoid freezing the UI
    def scan_thread():
        def update_callback(result):
            dpg.set_value("result_text", result)
        
        nmap_scan(subnet, update_callback)
    
    threading.Thread(target=scan_thread, daemon=True).start()

# PORT SCANNER GUI
def port_scanner_gui():
    create_themes()  # Create themes only once

    # Delete the existing window if it exists
    if dpg.does_item_exist("main_window"):
        dpg.delete_item("main_window")

    with dpg.window(tag="main_window", label="Port Scanner", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
        dpg.add_text("Port Scanner", tag="ps", color=(255, 255, 255, 255))
        dpg.add_separator(tag="separator")
        dpg.add_text("Enter The IP Address Here:", tag="ip_text", color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input", height=30, width=200, hint="e.g. 192.168.1.100")
        dpg.add_button(label="Scan", tag="scan_button_ps", pos=(0, 0), width=100, height=30, callback=run_port_scan)
        dpg.add_button(label="Back", tag="back_button_ps", pos=(0, 0), width=100, height=30, callback=return_to_home)
        dpg.add_input_text(tag="result_text", multiline=True, readonly=True, default_value="", width=700, height=200)

        # Bind Themes
        dpg.bind_item_theme("scan_button_ps", "button_theme")
        dpg.bind_item_theme("input", "input_theme")
        dpg.bind_item_theme("back_button_ps", "button_theme")
        dpg.bind_item_theme("result_text", "input_theme_result")
        dpg.bind_item_font("ps", setUp())

    port_scanner_resize()
    dpg.set_viewport_resize_callback(lambda: port_scanner_resize())
    dpg.hide_item("main_window_home")

def port_scanner_resize():
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("main_window", width)
    dpg.set_item_height("main_window", height)
    
    dpg.set_item_pos("ip_text", [(width / 2) - 200, (height / 2) - 40])
    dpg.set_item_pos("input", [(width / 2) - 10, (height / 2) - 40])
    dpg.set_item_pos("scan_button_ps", [(width / 2) - 10, (height / 2) - 0])
    dpg.set_item_pos("back_button_ps", [width - 120, 10])
    dpg.set_item_pos("result_text", [(width / 2) - 390, (height / 2) + 50])

def run_port_scan():
    ip_address = dpg.get_value("input")
    if not ip_address:
        dpg.set_value("result_text", "Please enter an IP address to scan.")
        return
        
    dpg.set_value("result_text", "Starting port scan...")
    
    # Run port scan in a separate thread to avoid freezing the UI
    def scan_thread():
        def update_callback(result):
            dpg.set_value("result_text", result)
        
        port_scanner(ip_address, update_callback)
    
    threading.Thread(target=scan_thread, daemon=True).start()

# WEB DIRECTORY SCANNER GUI
def webdir_scanner_gui():
    # Delete existing window if it exists to avoid duplicate windows
    if dpg.does_item_exist("main_window"):
        dpg.delete_item("main_window")

    with dpg.window(tag="main_window", label="Web Sub-directory Scanner", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
        dpg.add_text("Web Sub-directory Scanner", tag="wss", color=(255, 255, 255, 255))
        dpg.add_separator(tag="separator")
        dpg.add_text("Enter The URL Here:", tag="ip_text", color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input", height=30, width=200, hint="e.g. https://example.com")
        dpg.add_text("Select Wordlist:", tag='ws_text', color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input_ws", readonly=True, default_value="", height=30, width=200)
        dpg.add_button(label="Scan", tag="scan_button_ws", pos=(0, 0), width=100, height=30, callback=run_webdir_scan)
        dpg.add_button(label="Browse", tag="browse_button_ws", pos=(0, 0), width=100, height=30, callback=browse_wordlist)
        dpg.add_button(label="Back", tag="back_button_ws", pos=(0, 0), width=100, height=30, callback=return_to_home)
        dpg.add_input_text(tag="result_text", multiline=True, readonly=True, default_value="", width=700, height=200)

        # Create themes if they don't already exist
        create_themes()

        # Bind themes to the UI components
        dpg.bind_item_theme("scan_button_ws", "button_theme")
        dpg.bind_item_theme("input", "input_theme")
        dpg.bind_item_theme("input_ws", "input_ws_theme")
        dpg.bind_item_theme("browse_button_ws", "button_theme")
        dpg.bind_item_theme("back_button_ws", "button_theme")
        dpg.bind_item_theme("result_text", "input_theme_result")
        dpg.bind_item_font("wss", setUp())

    # Call resize after the window is created
    webdir_scanner_resize()
    dpg.set_viewport_resize_callback(lambda: webdir_scanner_resize())
    dpg.hide_item("main_window_home")

def webdir_scanner_resize():
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

def run_webdir_scan():
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
    def scan_thread():
        def update_callback(result):
            dpg.set_value("result_text", result)
        
        find_subdirectories(url, wordlist_file, update_callback)
    
    threading.Thread(target=scan_thread, daemon=True).start()

# COMMON FUNCTIONS
def return_to_home():
    dpg.hide_item("main_window")
    dpg.show_item("main_window_home")

def create_themes():
    # Create button theme
    if not dpg.does_item_exist("button_theme"):
        with dpg.theme(tag="button_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (22, 234, 147, 180))  # Background color
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 128, 0))  # Hover color
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (66, 150, 250, 255))  # Active color
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))  # Text color
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)  # Padding

    # Create input theme
    if not dpg.does_item_exist("input_theme"):
        with dpg.theme(tag="input_theme"):
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (22, 234, 147, 180))  # Dark green background
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))  # White text
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners

    # Create wordlist input theme
    if not dpg.does_item_exist("input_ws_theme"):
        with dpg.theme(tag="input_ws_theme"):
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (22, 234, 147, 180))  # Dark green background
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))  # White text
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners

    # Create result text theme
    if not dpg.does_item_exist("input_theme_result"):
        with dpg.theme(tag="input_theme_result"):
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (22, 234, 147, 180))  # Dark green background
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))  # Black text
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners

# MAIN APPLICATION ENTRY POINT
if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title='Network Security Scanner', width=800, height=600)
    dpg.setup_dearpygui()
    
    # Set the viewport background color
    dpg.set_viewport_clear_color((0, 0, 0, 255))

    # Initialize the home UI
    home_ui()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
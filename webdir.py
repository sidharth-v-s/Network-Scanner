import dearpygui.dearpygui as dpg
from fontsetup import setUp

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

def return_to_home():
    dpg.hide_item("main_window")
    dpg.show_item("main_window_home")

def webdirscanner():
    # Delete existing window if it exists to avoid duplicate windows
    if dpg.does_item_exist("main_window"):
        dpg.delete_item("main_window")

    with dpg.window(tag="main_window", label="Web Sub-directory Scanner", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
        dpg.add_text("Web Sub-directory Scanner", tag="wss", color=(255, 255, 255, 255))
        dpg.add_separator(tag="separator")
        dpg.add_text("Enter The URL Here:", tag="ip_text", color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input", height=30, width=200, multiline=True)
        dpg.add_text("Select Wordlist:", tag='ws_text', color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input_ws", readonly=True, default_value="", height=30, width=200, multiline=True)
        dpg.add_button(label="Scan", tag="scan_button_ws", pos=(0, 0), width=100, height=30)
        dpg.add_button(label="Browse", tag="browse_button_ws", pos=(0, 0), width=100, height=30)
        dpg.add_button(label="Back", tag="back_button_ws", pos=(0, 0), width=100, height=30, callback=return_to_home)
        dpg.add_input_text(tag="result_text", multiline=True, readonly=False, default_value="", width=700, height=200)

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
    resize()
    dpg.set_viewport_resize_callback(lambda: resize())

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

if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title='Web Sub-directory Scanner', width=800, height=600)
    dpg.setup_dearpygui()

    webdirscanner()

    dpg.show_viewport()
    dpg.start_dearpygui()

    dpg.destroy_context()

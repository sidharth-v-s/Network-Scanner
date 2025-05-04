import dearpygui.dearpygui as dpg
from fontsetup import setUp

def resize():
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("main_window", width)
    dpg.set_item_height("main_window", height)
    
    dpg.set_item_pos("ip_text", [(width / 2) - 200, (height / 2) - 40])
    dpg.set_item_pos("input", [(width / 2) - 10, (height / 2) - 40])
    dpg.set_item_pos("scan_button_ps", [(width / 2) - 10, (height / 2) - 0])
    dpg.set_item_pos("back_button_ps", [width - 120, 10])
    dpg.set_item_pos("separator", pos=(0, 0))
    dpg.set_item_pos("result_text", [(width / 2) - 390, (height / 2) + 50])

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

    # Create result text theme
    if not dpg.does_item_exist("input_theme_result"):
        with dpg.theme(tag="input_theme_result"):
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (22, 234, 147, 180))  # Dark green background
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))  # Black text
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners

def portscanner():
    create_themes()  # Create themes only once

    # Delete the existing window if it exists
    if dpg.does_item_exist("main_window"):
        dpg.delete_item("main_window")

    with dpg.window(tag="main_window", label="Port Scanner", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
        dpg.add_text("Port Scanner", tag="ps", color=(255, 255, 255, 255))
        dpg.add_separator(tag="separator")
        dpg.add_text("Enter The IP Address Here:", tag="ip_text", color=(255, 255, 255, 255))
        dpg.add_input_text(tag="input", height=30, width=200, multiline=True)
        dpg.add_button(label="Scan", tag="scan_button_ps", pos=(0, 0), width=100, height=30)
        dpg.add_button(label="Back", tag="back_button_ps", pos=(0, 0), width=100, height=30, callback=return_to_home)
        dpg.add_input_text(tag="result_text", multiline=True, readonly=True, default_value="", width=700, height=200)

        # Bind Themes
        dpg.bind_item_theme("scan_button_ps", "button_theme")
        dpg.bind_item_theme("input", "input_theme")
        dpg.bind_item_theme("back_button_ps", "button_theme")
        dpg.bind_item_theme("result_text", "input_theme_result")
        dpg.bind_item_font("ps", setUp())

    resize()
    dpg.set_viewport_resize_callback(lambda: resize())

if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title='Port Scanner', width=800, height=600)
    dpg.setup_dearpygui()

    portscanner()

    # Set the global background color to match the theme
    dpg.set_viewport_clear_color((0, 0, 0, 255))

    dpg.show_viewport()
    dpg.start_dearpygui()

    dpg.destroy_context()

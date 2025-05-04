import dearpygui.dearpygui as dpg

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

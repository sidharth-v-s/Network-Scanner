import dearpygui.dearpygui as dpg
from fontsetup import setUp
from hostlookup import hostlookupgui
from portscanner import portscanner
from webdir import webdirscanner
from themes import create_themes

def resize():
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("main_window_home", width)
    dpg.set_item_height("main_window_home", height)
    dpg.set_item_pos("exit_button", [width - 120, 10])
    dpg.set_item_pos("hlu_button_home", [(width / 2) - 95, (height / 2) - 150])
    dpg.set_item_pos("ps_button_home", [(width / 2) - 95, (height / 2) - 75])
    dpg.set_item_pos("sdf_button_home", [(width / 2) - 95, (height / 2) - 0])


def homeui():
    if dpg.does_item_exist("main_window_home"):
        dpg.show_item("main_window_home")
    else:
        with dpg.window(tag="main_window_home", label="INFO GATHER", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
            dpg.add_text("Network Security Scanner", tag="mh", color=(255, 255, 255, 255))
            dpg.add_separator()

            # Get the current viewport size
            width = dpg.get_viewport_width()
            height = dpg.get_viewport_height()

            dpg.add_button(label="Host Look Up", tag="hlu_button_home", pos=(0, 0), width=190, height=40, callback=hostlookupgui)
            dpg.add_button(label="Port Scanner", tag="ps_button_home", pos=(0, 50), width=190, height=40, callback=portscanner)
            dpg.add_button(label="Web Subdirectory Finder", tag="sdf_button_home", pos=(0, 100), width=190, height=40, callback=webdirscanner)
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

if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title='Network Security Scanner', width=800, height=600)
    dpg.setup_dearpygui()
    
    # Set the viewport background color
    dpg.set_viewport_clear_color((0, 0, 0, 255))

    homeui()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

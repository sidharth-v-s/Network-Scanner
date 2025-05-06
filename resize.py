import dearpygui.dearpygui as dpg
def homeResize():
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("main_window_home", width)
    dpg.set_item_height("main_window_home", height)
    dpg.set_item_pos("exit_button", [width - 120, 10])
    dpg.set_item_pos("hlu_button_home", [(width / 2) - 95, (height / 2) - 150])
    dpg.set_item_pos("ps_button_home", [(width / 2) - 95, (height / 2) - 75])
    dpg.set_item_pos("sdf_button_home", [(width / 2) - 95, (height / 2) - 0])
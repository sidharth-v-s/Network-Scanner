import dearpygui.dearpygui as dpg
def home_resize():
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("main_window_home", width)
    dpg.set_item_height("main_window_home", height)

    dpg.set_item_pos("hlu_button_home", [(width / 2) - 60, (height / 2) - 40])
    dpg.set_item_pos("ps_button_home", [(width / 2) - 60, (height / 2) + 20])
    dpg.set_item_pos("sdf_button_home", [(width / 2) - 60, (height / 2) + 80])
    dpg.set_item_pos("exit_button", [(width / 2) + 260, (height / 2) - 290])
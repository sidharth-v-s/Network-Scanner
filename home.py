import dearpygui.dearpygui as dpg
from fontsetup import setUp
def resize():
    width,height=dpg.get_viewport_width(),dpg.get_viewport_height()
    dpg.set_item_width("main_window",width)
    dpg.set_item_height("main_window",height)
    
    dpg.set_item_pos("hlu",[(width/2)-60,(height/2)-40])
    dpg.set_item_pos("ps",[(width/2)-60,(height/2)+20])
    dpg.set_item_pos("sdf",[(width/2)-60,(height/2)+80])
    
    
def home():
    with dpg.window(tag="main_window", label="INFO GATHER", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
        dpg.add_text("Network Scanner",tag="mh",color=(255,255,255,255))
        dpg.add_separator()
        
        dpg.add_button(label="Host Look Up", tag="hlu", pos=(0, 0), width=190, height=40)
        dpg.add_button(label="Port Scanner", tag="ps", pos=(0, 0), width=190, height=40)
        dpg.add_button(label="Web Subdirectory Finder", tag="sdf", pos=(0, 0), width=190, height=40)
        
        with dpg.theme(tag="button_theme"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (66, 100, 250, 255))  # Background color
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (66, 150, 250, 180))  # Hover color
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (66, 150, 250, 255))  # Active color
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))  # Text color
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)  # Padding
                    


        dpg.bind_item_theme("hlu", "button_theme")
        dpg.bind_item_theme("ps", "button_theme")
        dpg.bind_item_theme("sdf", "button_theme")
        dpg.bind_item_font("mh", setUp())
        resize()
        dpg.set_viewport_resize_callback(lambda:resize())

if __name__ =="__main__":
    dpg.create_context()
    dpg.create_viewport(title='InfoGatherTool',width=800,height=600)
    dpg.setup_dearpygui()
    
    home()
    
    dpg.show_viewport()
    dpg.start_dearpygui()
    
    dpg.destroy_context()
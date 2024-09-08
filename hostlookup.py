import dearpygui.dearpygui as dpg
from fontsetup import setUp

def resize():
    width,height=dpg.get_viewport_width(),dpg.get_viewport_height()
    dpg.set_item_width("main_window",width)
    dpg.set_item_height("main_window",height)
    
    dpg.set_item_pos("ip_text",[(width/3)-60,(height/2)-40])
    dpg.set_item_pos("input",[(width/2)-10,(height/2)-40])
    dpg.set_item_pos("scan_button",[(width/2)-10,(height/2)-0])
    
def hostlookupgui():
    with dpg.window(tag="main_window",label="host look up",pos=(0,0),no_title_bar=True,no_resize=True,no_move=True):
        dpg.add_text("Host Look Up Tool",tag="hlup",color=(255,255,255,255))
        dpg.add_text("Enter The Subnet Here:",tag="ip_text",color=(255,255,255,255))
        dpg.add_input_text(tag="input",height=30, width=200, multiline=True)
        dpg.add_button(label="Scan",tag="scan_button",pos=(0,0),width=100,height=30)
        
        

        with dpg.theme(tag="button_theme"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (22, 234, 147, 180))  # Background color
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 128, 0))  # Hover color
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (66, 150, 250, 255))  # Active color
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))  # Text color
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)  # Padding
                    
        with dpg.theme(tag="input_theme"):
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 128, 0))  # Dark green background
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))  # White text
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners
        
        
                    
                    
    dpg.bind_item_theme("scan_button", "button_theme")
    dpg.bind_item_theme("input", "input_theme")
    dpg.bind_item_font("hlup",setUp())
    resize()
    dpg.set_viewport_resize_callback(lambda:resize())
if __name__=="__main__":
    dpg.create_context()
    dpg.create_viewport(title='Host Look Up',width=800,height=600)
    dpg.setup_dearpygui()
        
    hostlookupgui()
        
    dpg.show_viewport()
    dpg.start_dearpygui()
        
    dpg.destroy_context()
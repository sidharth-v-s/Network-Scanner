from pathlib import Path
import os
import dearpygui.dearpygui as dpg

BASE_DIR = Path(__file__).resolve().parent
arial = None

def setUp():
    global arial
    if arial is None:
        with dpg.font_registry():
            arial = dpg.add_font(os.path.join(BASE_DIR,"arialbd.ttf"), 30)
    return arial

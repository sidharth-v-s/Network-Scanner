from pathlib import Path
import os
import dearpygui.dearpygui as dpg

BASE_DIR = Path(__file__).resolve().parent
FONT_FILE = os.path.join(BASE_DIR, "arialbd.ttf")

_fonts = {}


def setUp():
    """Legacy entrypoint — returns the default (30pt) heading font."""
    return get_font("heading")


def get_font(name: str = "body"):
    """Return a cached font handle. Sizes: heading(30) / subheading(20) / body(16)."""
    sizes = {"heading": 30, "subheading": 20, "body": 16, "small": 14}
    size = sizes.get(name, 16)

    if name not in _fonts:
        with dpg.font_registry():
            _fonts[name] = dpg.add_font(FONT_FILE, size)
    return _fonts[name]

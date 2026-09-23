"""
ui_widgets.py — Reusable DearPyGui building blocks shared across screens.

Keeping these in one place is what lets every tool screen look and feel
consistent (same card style, same section headers, same status pill)
without copy-pasting layout code four times.
"""

import dearpygui.dearpygui as dpg
import themes


def section_header(text: str, parent=None):
    kwargs = {"parent": parent} if parent else {}
    dpg.add_text(text.upper(), color=themes.TEXT_SECONDARY, **kwargs)
    dpg.add_spacer(height=2, **kwargs)


def card_start(tag: str, width: int = -1, height: int = 0):
    """Open a themed 'card' child window. Caller must call dpg.pop_container_stack() after adding contents (context manager preferred, see card())."""
    child = dpg.child_window(tag=tag, width=width, height=height, autosize_y=(height == 0))
    dpg.bind_item_theme(tag, "card_theme")
    return child


def card(tag: str, width: int = -1, height: int = 0):
    """Context-manager form: `with card("my_card"): ...`"""
    cw = dpg.child_window(tag=tag, width=width, height=height, autosize_y=(height == 0))
    dpg.bind_item_theme(tag, "card_theme")
    return cw


def primary_button(label, tag=None, callback=None, width=-1, height=34, user_data=None):
    kwargs = {}
    if tag:
        kwargs["tag"] = tag
    b = dpg.add_button(label=label, callback=callback, width=width, height=height,
                        user_data=user_data, **kwargs)
    dpg.bind_item_theme(b, "button_theme")
    return b


def secondary_button(label, tag=None, callback=None, width=-1, height=34, user_data=None):
    kwargs = {}
    if tag:
        kwargs["tag"] = tag
    b = dpg.add_button(label=label, callback=callback, width=width, height=height,
                        user_data=user_data, **kwargs)
    dpg.bind_item_theme(b, "button_theme_secondary")
    return b


def danger_button(label, tag=None, callback=None, width=-1, height=34, user_data=None):
    kwargs = {}
    if tag:
        kwargs["tag"] = tag
    b = dpg.add_button(label=label, callback=callback, width=width, height=height,
                        user_data=user_data, **kwargs)
    dpg.bind_item_theme(b, "button_theme_danger")
    return b


def labeled_input(label, tag, hint="", width=-1):
    dpg.add_text(label, color=themes.TEXT_SECONDARY)
    inp = dpg.add_input_text(tag=tag, hint=hint, width=width)
    dpg.bind_item_theme(inp, "input_theme")
    return inp


def status_pill(tag: str, default_text: str = "Idle"):
    """A small colored status indicator + text, updated via set_status()."""
    with dpg.group(horizontal=True, tag=f"{tag}_group"):
        dpg.add_text("\u2022", tag=f"{tag}_dot", color=themes.TEXT_DISABLED)
        dpg.add_text(default_text, tag=tag, color=themes.TEXT_SECONDARY)


def set_status(tag: str, text: str, kind: str = "muted"):
    color = themes.status_color(kind)
    if dpg.does_item_exist(tag):
        dpg.set_value(tag, text)
        dpg.configure_item(tag, color=color)
    if dpg.does_item_exist(f"{tag}_dot"):
        dpg.configure_item(f"{tag}_dot", color=color)


def progress(tag: str, width: int = -1):
    p = dpg.add_progress_bar(tag=tag, width=width, default_value=0.0, overlay="")
    dpg.bind_item_theme(p, "progress_theme")
    return p


def set_progress(tag: str, fraction: float, overlay: str = ""):
    if dpg.does_item_exist(tag):
        dpg.set_value(tag, max(0.0, min(1.0, fraction)))
        dpg.configure_item(tag, overlay=overlay)

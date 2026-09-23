"""
themes.py — Centralized visual theming for Network Security Scanner.

Provides a modern dark "cyber" theme with a consistent accent color,
rounded controls, subtle borders, and dedicated styles for status text
(success / warning / error / info), cards, sidebar nav, and data tables.
"""

import dearpygui.dearpygui as dpg

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BG_DARKEST = (13, 17, 23, 255)      # app background
BG_PANEL = (18, 24, 32, 255)        # sidebar / cards
BG_INPUT = (25, 32, 43, 255)        # input fields
BG_INPUT_HOVER = (32, 41, 54, 255)
BORDER = (46, 58, 74, 255)

ACCENT = (0, 230, 168, 255)         # signature green/teal
ACCENT_HOVER = (35, 245, 190, 255)
ACCENT_ACTIVE = (0, 190, 138, 255)
ACCENT_DIM = (0, 230, 168, 60)

TEXT_PRIMARY = (230, 236, 240, 255)
TEXT_SECONDARY = (140, 155, 170, 255)
TEXT_DISABLED = (90, 100, 112, 255)

SUCCESS = (76, 217, 123, 255)
WARNING = (255, 187, 76, 255)
ERROR = (255, 92, 92, 255)
INFO = (99, 179, 255, 255)

SEVERITY_COLORS = {
    "open": SUCCESS,
    "closed": TEXT_DISABLED,
    "filtered": WARNING,
    "error": ERROR,
    "info": INFO,
}


def _ensure(tag):
    return not dpg.does_item_exist(tag)


def create_themes():
    """Idempotent: safe to call multiple times."""

    # ---------------- Global app theme ----------------
    if _ensure("global_theme"):
        with dpg.theme(tag="global_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, BG_DARKEST)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BG_DARKEST)
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, BG_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
                dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_PRIMARY)
                dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, TEXT_DISABLED)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, BG_DARKEST)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, BORDER)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, ACCENT_DIM)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, ACCENT)
                dpg.add_theme_color(dpg.mvThemeCol_Separator, BORDER)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, BG_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, BG_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ACCENT)
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, ACCENT)
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, ACCENT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_Header, ACCENT_DIM)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (0, 230, 168, 90))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 230, 168, 120))
                dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, BG_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, BORDER)
                dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, (30, 38, 48, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, BG_DARKEST)
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (17, 22, 29, 255))
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 8)

    # ---------------- Primary (accent) button ----------------
    if _ensure("button_theme"):
        with dpg.theme(tag="button_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_ACTIVE)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (7, 15, 12, 255))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 14, 8)

    # ---------------- Secondary / ghost button ----------------
    if _ensure("button_theme_secondary"):
        with dpg.theme(tag="button_theme_secondary"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, BG_INPUT)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, BG_INPUT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, BORDER)
                dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_PRIMARY)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 14, 8)

    # ---------------- Danger button (stop / cancel) ----------------
    if _ensure("button_theme_danger"):
        with dpg.theme(tag="button_theme_danger"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (66, 26, 26, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (110, 35, 35, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (140, 40, 40, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, ERROR)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 14, 8)

    # ---------------- Nav (sidebar) button — flatter, left aligned ----------------
    if _ensure("nav_button_theme"):
        with dpg.theme(tag="nav_button_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, BG_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, BG_INPUT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_DIM)
                dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_SECONDARY)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 12, 10)

    if _ensure("nav_button_theme_active"):
        with dpg.theme(tag="nav_button_theme_active"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_DIM)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, ACCENT_DIM)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, ACCENT_DIM)
                dpg.add_theme_color(dpg.mvThemeCol_Text, ACCENT)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 12, 10)

    # ---------------- Text inputs ----------------
    if _ensure("input_theme"):
        with dpg.theme(tag="input_theme"):
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, BG_INPUT)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, BG_INPUT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, BG_INPUT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_PRIMARY)
                dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)

    if _ensure("input_theme_result"):
        # Monospace-ish log/result readonly box
        with dpg.theme(tag="input_theme_result"):
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (9, 12, 16, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (150, 235, 195, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)

    if _ensure("combo_theme"):
        with dpg.theme(tag="combo_theme"):
            with dpg.theme_component(dpg.mvCombo):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, BG_INPUT)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, BG_INPUT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, BG_INPUT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_PRIMARY)
                dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)

    if _ensure("checkbox_theme"):
        with dpg.theme(tag="checkbox_theme"):
            with dpg.theme_component(dpg.mvCheckbox):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, BG_INPUT)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, BG_INPUT_HOVER)
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, ACCENT)

    # ---------------- Cards / panels ----------------
    if _ensure("card_theme"):
        with dpg.theme(tag="card_theme"):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BG_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 16, 14)

    if _ensure("sidebar_theme"):
        with dpg.theme(tag="sidebar_theme"):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BG_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 16)

    # ---------------- Progress bar ----------------
    if _ensure("progress_theme"):
        with dpg.theme(tag="progress_theme"):
            with dpg.theme_component(dpg.mvProgressBar):
                dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, ACCENT)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, BG_INPUT)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    # ---------------- Table ----------------
    if _ensure("table_theme"):
        with dpg.theme(tag="table_theme"):
            with dpg.theme_component(dpg.mvTable):
                dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, BG_INPUT)
                dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, BORDER)
                dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, (28, 36, 46, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, BG_DARKEST)
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (17, 22, 29, 255))

    dpg.bind_theme("global_theme")


def status_color(kind: str):
    """Return an RGBA color tuple for a semantic status kind."""
    return {
        "success": SUCCESS,
        "warning": WARNING,
        "error": ERROR,
        "info": INFO,
        "muted": TEXT_SECONDARY,
    }.get(kind, TEXT_PRIMARY)

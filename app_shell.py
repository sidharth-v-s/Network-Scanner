"""
app_shell.py — Application shell: sidebar navigation + swappable content pane.

Replaces the old pattern (every screen module deleting/recreating a window
called "main_window" and manually repositioning every widget on resize).
Instead there is ONE persistent layout:

    +----------------+-------------------------------------+
    |                |                                       |
    |    SIDEBAR     |          CONTENT (per-screen)         |
    |  (nav buttons) |                                       |
    |                |                                       |
    +----------------+-------------------------------------+

Screens register a `build(content_parent)` function; navigating just
clears the content child window and calls the target screen's builder.
DearPyGui's native table/child-window layout handles resizing for free,
so there's no manual pixel-position bookkeeping anymore.
"""

import dearpygui.dearpygui as dpg
import themes
import fontsetup
import scan_history

SIDEBAR_WIDTH = 240

_screens = {}      # name -> build(content_parent) callable
_nav_buttons = {}  # name -> button tag
_current_screen = None


def register_screen(name, icon, build_fn):
    _screens[name] = {"build": build_fn, "icon": icon}


def _clear_content():
    if dpg.does_item_exist("content_area"):
        dpg.delete_item("content_area", children_only=True)


def navigate(screen_name):
    global _current_screen
    if screen_name not in _screens:
        return
    _current_screen = screen_name

    for name, tag in _nav_buttons.items():
        dpg.bind_item_theme(tag, "nav_button_theme_active" if name == screen_name else "nav_button_theme")

    _clear_content()
    _screens[screen_name]["build"]("content_area")


def build_shell():
    themes.create_themes()

    with dpg.window(tag="root_window", label="Network Security Scanner",
                     no_title_bar=True, no_resize=True, no_move=True, no_collapse=True):
        with dpg.group(horizontal=True):
            # -------------------- Sidebar --------------------
            with dpg.child_window(tag="sidebar", width=SIDEBAR_WIDTH, border=True):
                dpg.bind_item_theme("sidebar", "sidebar_theme")

                with dpg.group():
                    dpg.add_text("NET//SCANNER", color=themes.ACCENT)
                    dpg.add_text("Recon Toolkit v3", color=themes.TEXT_DISABLED)
                dpg.add_spacer(height=12)
                dpg.add_separator()
                dpg.add_spacer(height=12)

                for name in ["Dashboard", "Host Discovery", "Port Scanner",
                             "Web Directory Scan", "Quick Recon", "Scan History"]:
                    tag = f"nav_{name.replace(' ', '_')}"
                    icon = _screens.get(name, {}).get("icon", "")
                    b = dpg.add_button(label=f"{icon}  {name}", tag=tag, width=-1, height=38,
                                        callback=lambda s, a, u: navigate(u), user_data=name)
                    dpg.bind_item_theme(tag, "nav_button_theme")
                    _nav_buttons[name] = tag

                dpg.add_spacer(height=1)
                with dpg.child_window(border=False, height=-40):
                    pass  # spacer pushes footer down
                dpg.add_separator()
                dpg.add_text("Use only on systems you\nown or are authorized\nto test.",
                              color=themes.TEXT_DISABLED, wrap=SIDEBAR_WIDTH - 24)
                exit_btn = dpg.add_button(label="Exit", tag="exit_button", width=-1, height=30,
                                           callback=lambda: dpg.stop_dearpygui())
                dpg.bind_item_theme(exit_btn, "button_theme_secondary")

            # -------------------- Content --------------------
            with dpg.child_window(tag="content_area", border=False):
                pass

    dpg.set_primary_window("root_window", True)
    navigate("Dashboard")


def resize_shell():
    if not dpg.does_item_exist("root_window"):
        return
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_width("root_window", width)
    dpg.set_item_height("root_window", height)


# ---------------------------------------------------------------------------
# Dashboard screen (home)
# ---------------------------------------------------------------------------

def _dashboard_card(title, desc, screen_name, icon):
    with dpg.child_window(width=340, height=180, no_scrollbar=True, no_scroll_with_mouse=True):
        dpg.bind_item_theme(dpg.last_item(), "card_theme")
        dpg.add_text(f"{icon}  {title}", color=themes.ACCENT)
        dpg.add_spacer(height=6)
        dpg.add_text(desc, wrap=300, color=themes.TEXT_SECONDARY)
        dpg.add_spacer(height=10)
        b = dpg.add_button(label="Open ->", width=-1, callback=lambda: navigate(screen_name))
        dpg.bind_item_theme(b, "button_theme_secondary")


def build_dashboard(parent):
    with dpg.group(parent=parent):
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group():
                dpg.add_text("Network Security Scanner", color=themes.TEXT_PRIMARY)
                dpg.bind_item_font(dpg.last_item(), fontsetup.get_font("heading"))
                dpg.add_text("Recon toolkit for authorized security testing & CTF practice",
                              color=themes.TEXT_SECONDARY)
        dpg.add_spacer(height=24)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group(horizontal=True):
                _dashboard_card("Host Discovery", "Ping-sweep a subnet to find live hosts, "
                                 "hostnames, MAC addresses, and hardware vendors.",
                                 "Host Discovery", "[NET]")
                dpg.add_spacer(width=16)
                _dashboard_card("Port Scanner", "Scan a target for open ports, running "
                                 "services, versions, and OS fingerprint via nmap.",
                                 "Port Scanner", "[SCAN]")
        dpg.add_spacer(height=16)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group(horizontal=True):
                _dashboard_card("Web Directory Scan", "Brute-force hidden directories and "
                                 "files on a web server using a custom wordlist.",
                                 "Web Directory Scan", "[WEB]")
                dpg.add_spacer(width=16)
                _dashboard_card("Quick Recon", "Run host discovery + a fast port scan "
                                 "across a whole subnet in one guided workflow.",
                                 "Quick Recon", "[FAST]")

        dpg.add_spacer(height=24)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=696, height=180):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                dpg.add_text("Recent Activity", color=themes.TEXT_PRIMARY)
                dpg.add_separator()
                history = scan_history.load_history()[-6:][::-1]
                if not history:
                    dpg.add_text("No scans yet. Run a tool from the sidebar to get started.",
                                  color=themes.TEXT_DISABLED)
                else:
                    for entry in history:
                        with dpg.group(horizontal=True):
                            dpg.add_text(entry["timestamp"].split("T")[1][:8], color=themes.TEXT_DISABLED)
                            dpg.add_text(entry["type"], color=themes.ACCENT)
                            dpg.add_text(entry["target"], color=themes.TEXT_PRIMARY)
                            dpg.add_text(f"— {entry['summary']}", color=themes.TEXT_SECONDARY)

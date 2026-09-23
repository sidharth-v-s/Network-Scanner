"""
history_view.py — Scan History screen.

Browses the persistent local scan log written by scan_history.py so users
can review what they've already scanned across sessions (useful when
working through a lab or CTF box over multiple sittings).
"""

import dearpygui.dearpygui as dpg

import scan_history
import themes
import ui_widgets


def _refresh():
    if dpg.does_item_exist("hist_table"):
        dpg.delete_item("hist_table", children_only=True, slot=1)

    entries = list(reversed(scan_history.load_history()))
    if not entries:
        with dpg.table_row(parent="hist_table"):
            dpg.add_text("—")
            dpg.add_text("No scans recorded yet.", color=themes.TEXT_DISABLED)
            dpg.add_text("")
            dpg.add_text("")
        return

    for entry in entries:
        with dpg.table_row(parent="hist_table"):
            dpg.add_text(entry.get("timestamp", "").replace("T", " "), color=themes.TEXT_SECONDARY)
            dpg.add_text(entry.get("type", ""), color=themes.ACCENT)
            dpg.add_text(entry.get("target", ""), color=themes.TEXT_PRIMARY)
            dpg.add_text(entry.get("summary", ""), color=themes.TEXT_SECONDARY)


def clear_history():
    scan_history.clear_history()
    _refresh()
    ui_widgets.set_status("hist_status", "History cleared.", "warning")


def build(parent):
    import fontsetup
    with dpg.group(parent=parent):
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group():
                dpg.add_text("Scan History")
                dpg.bind_item_font(dpg.last_item(), fontsetup.get_font("subheading"))
                dpg.add_text("A local log of every scan run from this app, stored in "
                              "~/.network_scanner/history.json.", color=themes.TEXT_SECONDARY)
        dpg.add_spacer(height=16)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group(horizontal=True):
                ui_widgets.secondary_button("Refresh", callback=lambda: _refresh(), width=120)
                ui_widgets.danger_button("Clear History", callback=clear_history, width=140)

        dpg.add_spacer(height=8)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            ui_widgets.status_pill("hist_status", "")

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=-24):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                with dpg.table(tag="hist_table", header_row=True, resizable=True,
                                borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                borders_outerV=True, scrollY=True, policy=dpg.mvTable_SizingStretchProp):
                    dpg.bind_item_theme("hist_table", "table_theme")
                    dpg.add_table_column(label="Timestamp")
                    dpg.add_table_column(label="Type")
                    dpg.add_table_column(label="Target")
                    dpg.add_table_column(label="Summary")
                    _refresh()

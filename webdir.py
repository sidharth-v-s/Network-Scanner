"""
webdir.py — Web Directory / File Scanner screen.

Over the original: real concurrency (thread pool instead of one request
at a time), proper cancellation, an optional extension list (.php,.bak,…),
a live progress bar with completed/total counts, a color-coded results
table by status code, and export.
"""

import threading

import dearpygui.dearpygui as dpg

import scan_engine
import scan_history
import themes
import ui_widgets

_cancel_token = scan_engine.ScanCancelToken()
_last_results = []

_STATUS_KIND = {
    2: "success",   # 2xx
    3: "info",      # 3xx
    4: "warning",   # 4xx (401/403 are often interesting, not fatal)
    5: "error",     # 5xx
}


def _status_kind(code: int) -> str:
    return _STATUS_KIND.get(code // 100, "muted")


def _set_scanning_ui(is_scanning: bool):
    dpg.configure_item("ws_scan_btn", enabled=not is_scanning)
    dpg.configure_item("ws_stop_btn", show=is_scanning)
    dpg.configure_item("ws_export_btn", enabled=(not is_scanning) and bool(_last_results))


def _clear_table():
    if dpg.does_item_exist("ws_table"):
        dpg.delete_item("ws_table", children_only=True, slot=1)


def _add_table_columns():
    dpg.add_table_column(label="Status")
    dpg.add_table_column(label="URL")
    dpg.add_table_column(label="Redirect")


def _add_dir_row(d):
    color = themes.status_color(_status_kind(d.status))
    with dpg.table_row(parent="ws_table"):
        dpg.add_text(str(d.status), color=color)
        dpg.add_text(d.url, color=themes.TEXT_PRIMARY)
        dpg.add_text(d.redirect_to or "—", color=themes.TEXT_SECONDARY)


def browse_wordlist():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Wordlist File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    root.destroy()
    if file_path:
        dpg.set_value("ws_wordlist_input", file_path)


def _parse_extensions():
    raw = dpg.get_value("ws_ext_input").strip()
    if not raw:
        return None
    exts = [e.strip() for e in raw.split(",") if e.strip()]
    exts = [e if e.startswith(".") else f".{e}" for e in exts]
    return exts


def run_scan():
    url = dpg.get_value("ws_url_input").strip()
    wordlist = dpg.get_value("ws_wordlist_input").strip()

    valid, err, normalized = scan_engine.validate_url(url)
    if not valid:
        ui_widgets.set_status("ws_status", err, "error")
        return
    if not wordlist:
        ui_widgets.set_status("ws_status", "Select a wordlist file first.", "error")
        return

    global _last_results
    _last_results = []
    _clear_table()
    _cancel_token.reset()
    _set_scanning_ui(True)
    ui_widgets.set_status("ws_status", f"Scanning {normalized} …", "info")
    ui_widgets.set_progress("ws_progress", 0.0, "")

    extensions = _parse_extensions()
    threads = int(dpg.get_value("ws_threads_input") or 20)

    def on_event(evt):
        kind = evt["kind"]
        if kind == "status":
            ui_widgets.set_status("ws_status", evt["message"], "info")
        elif kind == "error":
            ui_widgets.set_status("ws_status", evt["message"], "error")
            _set_scanning_ui(False)
        elif kind == "dir_found":
            d = evt["result"]
            _add_dir_row(d)
            _last_results.append(d)
        elif kind == "progress":
            frac = evt["completed"] / max(evt["total"], 1)
            ui_widgets.set_progress("ws_progress", frac, f"{evt['completed']}/{evt['total']}")
        elif kind == "cancelled":
            ui_widgets.set_status(
                "ws_status", f"Cancelled — {len(_last_results)} path(s) found so far.", "warning")
            _set_scanning_ui(False)
        elif kind == "complete":
            n = len(evt["results"])
            ui_widgets.set_status("ws_status", f"Done — {n} path(s) found in {evt['elapsed']:.1f}s.", "success")
            ui_widgets.set_progress("ws_progress", 1.0, "Complete")
            _set_scanning_ui(False)
            scan_history.add_entry("Web Directory Scan", normalized, f"{n} path(s) found")

    def worker():
        scan_engine.web_directory_scan(
            url, wordlist, on_event=on_event, cancel_token=_cancel_token,
            extensions=extensions, threads=threads,
        )

    threading.Thread(target=worker, daemon=True).start()


def stop_scan():
    _cancel_token.cancel()
    ui_widgets.set_status("ws_status", "Stopping …", "warning")


def export_results():
    if not _last_results:
        return
    import os
    from datetime import datetime
    export_dir = os.path.join(os.path.expanduser("~"), "network_scanner_exports")
    os.makedirs(export_dir, exist_ok=True)
    fname = f"web_dir_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(export_dir, fname)
    scan_engine.export_results("dirs", _last_results, path)
    ui_widgets.set_status("ws_status", f"Exported to {path}", "success")


def build(parent):
    import fontsetup
    with dpg.group(parent=parent):
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group():
                dpg.add_text("Web Directory Scanner")
                dpg.bind_item_font(dpg.last_item(), fontsetup.get_font("subheading"))
                dpg.add_text("Brute-force hidden directories and files on a web server.",
                              color=themes.TEXT_SECONDARY)
        dpg.add_spacer(height=16)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=275):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")

                ui_widgets.labeled_input("Target URL", "ws_url_input", hint="e.g. https://example.com", width=-1)
                dpg.add_spacer(height=8)

                with dpg.group(horizontal=True):
                    with dpg.group(width=-160):
                        dpg.add_text("Wordlist", color=themes.TEXT_SECONDARY)
                        wl = dpg.add_input_text(tag="ws_wordlist_input", readonly=True, width=-1)
                        dpg.bind_item_theme(wl, "input_theme")
                    dpg.add_spacer(width=8)
                    with dpg.group():
                        dpg.add_spacer(height=19)
                        ui_widgets.secondary_button("Browse…", callback=browse_wordlist, width=120)

                dpg.add_spacer(height=8)
                with dpg.group(horizontal=True):
                    with dpg.group(width=200):
                        dpg.add_text("Extensions (optional, comma-sep)", color=themes.TEXT_SECONDARY)
                        ext_in = dpg.add_input_text(tag="ws_ext_input", hint="php,bak,zip", width=-1)
                        dpg.bind_item_theme(ext_in, "input_theme")
                    dpg.add_spacer(width=16)
                    with dpg.group(width=100):
                        dpg.add_text("Threads", color=themes.TEXT_SECONDARY)
                        th_in = dpg.add_input_text(tag="ws_threads_input", default_value="20",
                                                    decimal=True, width=-1)
                        dpg.bind_item_theme(th_in, "input_theme")

                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    ui_widgets.primary_button("Scan", tag="ws_scan_btn", callback=run_scan, width=120)
                    ui_widgets.danger_button("Stop", tag="ws_stop_btn", callback=stop_scan, width=100)
                    dpg.configure_item("ws_stop_btn", show=False)
                    ui_widgets.secondary_button("Export CSV", tag="ws_export_btn",
                                                 callback=export_results, width=140)
                    dpg.configure_item("ws_export_btn", enabled=False)

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group(width=-24):
                ui_widgets.status_pill("ws_status", "Idle — enter a URL and wordlist to begin.")
                dpg.add_spacer(height=4)
                ui_widgets.progress("ws_progress")

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=-24):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                with dpg.table(tag="ws_table", header_row=True, resizable=True,
                                borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                borders_outerV=True, scrollY=True, policy=dpg.mvTable_SizingStretchProp):
                    dpg.bind_item_theme("ws_table", "table_theme")
                    _add_table_columns()

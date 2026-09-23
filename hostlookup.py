"""
hostlookup.py — Host Discovery screen.

Ping-sweeps a subnet/CIDR and renders discovered hosts as a live-updating
table (IP / hostname / MAC / vendor) instead of a flat text blob. Supports
cancellation mid-scan and exporting results to TXT/CSV/JSON.
"""

import threading

import dearpygui.dearpygui as dpg

import scan_engine
import scan_history
import themes
import ui_widgets

_cancel_token = scan_engine.ScanCancelToken()
_last_results = []


def _set_scanning_ui(is_scanning: bool):
    dpg.configure_item("hd_scan_btn", enabled=not is_scanning)
    dpg.configure_item("hd_stop_btn", show=is_scanning)
    dpg.configure_item("hd_export_btn", enabled=(not is_scanning) and bool(_last_results))


def _clear_table():
    if dpg.does_item_exist("hd_table"):
        dpg.delete_item("hd_table", children_only=True, slot=1)


def _add_table_columns():
    dpg.add_table_column(label="IP Address")
    dpg.add_table_column(label="Hostname")
    dpg.add_table_column(label="MAC Address")
    dpg.add_table_column(label="Vendor")


def _add_host_row(host):
    with dpg.table_row(parent="hd_table"):
        dpg.add_text(host.ip, color=themes.SUCCESS)
        dpg.add_text(host.hostname or "—", color=themes.TEXT_SECONDARY)
        dpg.add_text(host.mac or "—", color=themes.TEXT_SECONDARY)
        dpg.add_text(host.vendor or "—", color=themes.TEXT_SECONDARY)


def run_scan():
    subnet = dpg.get_value("hd_input").strip()
    resolve = dpg.get_value("hd_resolve_check")

    valid, err = scan_engine.validate_target(subnet)
    if not valid:
        ui_widgets.set_status("hd_status", err, "error")
        return

    global _last_results
    _last_results = []
    _clear_table()
    _cancel_token.reset()
    _set_scanning_ui(True)
    ui_widgets.set_status("hd_status", "Starting host discovery …", "info")
    ui_widgets.set_progress("hd_progress", 0.0, "")

    def on_event(evt):
        kind = evt["kind"]
        if kind == "status":
            ui_widgets.set_status("hd_status", evt["message"], "info")
        elif kind == "error":
            ui_widgets.set_status("hd_status", evt["message"], "error")
        elif kind == "host_found":
            _add_host_row(evt["host"])
            _last_results.append(evt["host"])
            frac = evt["index"] / max(evt["total"], 1)
            ui_widgets.set_progress("hd_progress", frac, f"{evt['index']}/{evt['total']}")
        elif kind == "cancelled":
            ui_widgets.set_status("hd_status", f"Cancelled — {len(_last_results)} host(s) found so far.", "warning")
            _set_scanning_ui(False)
        elif kind == "complete":
            n = len(evt["results"])
            ui_widgets.set_status("hd_status", f"Done — {n} host(s) found in {evt['elapsed']:.1f}s.", "success")
            ui_widgets.set_progress("hd_progress", 1.0, "Complete")
            _set_scanning_ui(False)
            scan_history.add_entry("Host Discovery", subnet, f"{n} host(s) found")

    def worker():
        scan_engine.host_discovery(
            subnet, on_event=on_event, cancel_token=_cancel_token, resolve_hostnames=resolve,
        )

    threading.Thread(target=worker, daemon=True).start()


def stop_scan():
    _cancel_token.cancel()
    ui_widgets.set_status("hd_status", "Stopping …", "warning")


def export_results():
    if not _last_results:
        return
    import os
    export_dir = os.path.join(os.path.expanduser("~"), "network_scanner_exports")
    os.makedirs(export_dir, exist_ok=True)
    from datetime import datetime
    fname = f"host_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(export_dir, fname)
    scan_engine.export_results("hosts", _last_results, path)
    ui_widgets.set_status("hd_status", f"Exported to {path}", "success")


def build(parent):
    with dpg.group(parent=parent):
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group():
                dpg.add_text("Host Discovery")
                import fontsetup
                dpg.bind_item_font(dpg.last_item(), fontsetup.get_font("subheading"))
                dpg.add_text("Ping-sweep a subnet to find live hosts and identify devices.",
                              color=themes.TEXT_SECONDARY)
        dpg.add_spacer(height=16)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=155):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                with dpg.group(horizontal=True):
                    with dpg.group(width=320):
                        ui_widgets.labeled_input("Subnet / CIDR / Range", "hd_input",
                                                  hint="e.g. 192.168.1.0/24")
                    dpg.add_spacer(width=16)
                    with dpg.group():
                        dpg.add_text("Options", color=themes.TEXT_SECONDARY)
                        chk = dpg.add_checkbox(label="Resolve hostnames (DNS)", tag="hd_resolve_check",
                                                default_value=True)
                        dpg.bind_item_theme(chk, "checkbox_theme")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    ui_widgets.primary_button("Scan", tag="hd_scan_btn", callback=run_scan, width=120)
                    ui_widgets.danger_button("Stop", tag="hd_stop_btn", callback=stop_scan, width=100)
                    dpg.configure_item("hd_stop_btn", show=False)
                    ui_widgets.secondary_button("Export CSV", tag="hd_export_btn",
                                                 callback=export_results, width=140)
                    dpg.configure_item("hd_export_btn", enabled=False)

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group(width=-24):
                ui_widgets.status_pill("hd_status", "Idle — enter a subnet to begin.")
                dpg.add_spacer(height=4)
                ui_widgets.progress("hd_progress")

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=-24):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                with dpg.table(tag="hd_table", header_row=True, resizable=True,
                                borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                borders_outerV=True, scrollY=True, policy=dpg.mvTable_SizingStretchProp):
                    dpg.bind_item_theme("hd_table", "table_theme")
                    _add_table_columns()

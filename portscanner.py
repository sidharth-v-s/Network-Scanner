"""
portscanner.py — Port Scanner screen.

Adds over the original: scan-profile presets, optional NSE script groups
(Nmap Scripting Engine — discovery / enumeration / vuln / auth), a live
color-coded results table, an OS-fingerprint panel, cancellation, and
export.
"""

import threading

import dearpygui.dearpygui as dpg

import scan_engine
import scan_history
import themes
import ui_widgets

_cancel_token = scan_engine.ScanCancelToken()
_last_result = None


def _set_scanning_ui(is_scanning: bool):
    dpg.configure_item("ps_scan_btn", enabled=not is_scanning)
    dpg.configure_item("ps_stop_btn", show=is_scanning)
    dpg.configure_item("ps_export_btn", enabled=(not is_scanning) and bool(_last_result and _last_result.ports))


def _clear_table():
    if dpg.does_item_exist("ps_table"):
        dpg.delete_item("ps_table", children_only=True, slot=1)
    if dpg.does_item_exist("ps_os_text"):
        dpg.set_value("ps_os_text", "")


def _add_table_columns():
    dpg.add_table_column(label="Port")
    dpg.add_table_column(label="Proto")
    dpg.add_table_column(label="State")
    dpg.add_table_column(label="Service / Version")


def _add_port_row(p):
    color = themes.SEVERITY_COLORS.get(p.state, themes.TEXT_PRIMARY)
    with dpg.table_row(parent="ps_table"):
        dpg.add_text(str(p.port), color=color)
        dpg.add_text(p.protocol, color=themes.TEXT_SECONDARY)
        dpg.add_text(p.state.upper(), color=color)
        dpg.add_text(p.display_service, color=themes.TEXT_PRIMARY)


def _selected_nse_scripts():
    scripts = []
    for group, items in scan_engine.NSE_SCRIPT_GROUPS.items():
        tag = f"ps_nse_{group}"
        if dpg.does_item_exist(tag) and dpg.get_value(tag):
            scripts.extend(items)
    return scripts


def run_scan():
    target = dpg.get_value("ps_input").strip()
    profile = dpg.get_value("ps_profile_combo")

    valid, err = scan_engine.validate_target(target)
    if not valid:
        ui_widgets.set_status("ps_status", err, "error")
        return

    global _last_result
    _last_result = None
    _clear_table()
    _cancel_token.reset()
    _set_scanning_ui(True)
    ui_widgets.set_status("ps_status", "Starting scan …", "info")
    ui_widgets.set_progress("ps_progress", 0.15, "Scanning…")

    base_args = scan_engine.SCAN_PROFILES.get(profile, "-A -T4")
    scripts = _selected_nse_scripts()
    scan_arguments = scan_engine.build_nse_arguments(base_args, scripts)

    def on_event(evt):
        kind = evt["kind"]
        if kind == "status":
            ui_widgets.set_status("ps_status", evt["message"], "info")
        elif kind == "error":
            ui_widgets.set_status("ps_status", evt["message"], "error")
            ui_widgets.set_progress("ps_progress", 0.0, "")
            _set_scanning_ui(False)
        elif kind == "port_found":
            _add_port_row(evt["port"])
        elif kind == "cancelled":
            ui_widgets.set_status("ps_status", "Scan cancelled.", "warning")
            _set_scanning_ui(False)
        elif kind == "complete":
            global _last_result
            result = evt["results"]
            _last_result = result
            open_count = sum(1 for p in result.ports if p.state == "open")
            ui_widgets.set_status(
                "ps_status",
                f"Done — {open_count} open port(s) in {evt['elapsed']:.1f}s.", "success",
            )
            ui_widgets.set_progress("ps_progress", 1.0, "Complete")

            if result.os_matches:
                os_lines = [f"{m['name']}  ({m['accuracy']}% confidence)" for m in result.os_matches]
                dpg.set_value("ps_os_text", "OS Guess:\n" + "\n".join(os_lines))
            if result.mac:
                mac_line = f"MAC: {result.mac}"
                if result.vendor:
                    mac_line += f"  ({result.vendor})"
                dpg.set_value("ps_mac_text", mac_line)

            _set_scanning_ui(False)
            scan_history.add_entry("Port Scan", target, f"{open_count} open port(s)")

    def worker():
        scan_engine.port_scan(target, on_event=on_event, cancel_token=_cancel_token,
                               scan_arguments=scan_arguments)

    threading.Thread(target=worker, daemon=True).start()


def stop_scan():
    _cancel_token.cancel()
    ui_widgets.set_status("ps_status", "Stopping …", "warning")


def export_results():
    if not (_last_result and _last_result.ports):
        return
    import os
    from datetime import datetime
    export_dir = os.path.join(os.path.expanduser("~"), "network_scanner_exports")
    os.makedirs(export_dir, exist_ok=True)
    fname = f"port_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(export_dir, fname)
    scan_engine.export_results("ports", _last_result.ports, path)
    ui_widgets.set_status("ps_status", f"Exported to {path}", "success")


def build(parent):
    import fontsetup
    with dpg.group(parent=parent):
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group():
                dpg.add_text("Port Scanner")
                dpg.bind_item_font(dpg.last_item(), fontsetup.get_font("subheading"))
                dpg.add_text("Discover open ports, services, versions, and OS fingerprint.",
                              color=themes.TEXT_SECONDARY)
        dpg.add_spacer(height=16)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=245):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                with dpg.group(horizontal=True):
                    with dpg.group(width=320):
                        ui_widgets.labeled_input("Target IP / Host", "ps_input",
                                                  hint="e.g. 192.168.1.100")
                    dpg.add_spacer(width=16)
                    with dpg.group(width=280):
                        dpg.add_text("Scan Profile", color=themes.TEXT_SECONDARY)
                        combo = dpg.add_combo(list(scan_engine.SCAN_PROFILES.keys()),
                                               default_value="Quick (top 100 ports)",
                                               tag="ps_profile_combo", width=-1)
                        dpg.bind_item_theme(combo, "combo_theme")

                dpg.add_spacer(height=10)
                dpg.add_text("NSE Script Groups (optional)", color=themes.TEXT_SECONDARY)
                with dpg.group(horizontal=True):
                    for group in scan_engine.NSE_SCRIPT_GROUPS:
                        chk = dpg.add_checkbox(label=group, tag=f"ps_nse_{group}")
                        dpg.bind_item_theme(chk, "checkbox_theme")

                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    ui_widgets.primary_button("Scan", tag="ps_scan_btn", callback=run_scan, width=120)
                    ui_widgets.danger_button("Stop", tag="ps_stop_btn", callback=stop_scan, width=100)
                    dpg.configure_item("ps_stop_btn", show=False)
                    ui_widgets.secondary_button("Export CSV", tag="ps_export_btn",
                                                 callback=export_results, width=140)
                    dpg.configure_item("ps_export_btn", enabled=False)

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group(width=-24):
                ui_widgets.status_pill("ps_status", "Idle — enter a target to begin.")
                dpg.add_spacer(height=4)
                ui_widgets.progress("ps_progress")

        dpg.add_spacer(height=8)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            dpg.add_text("", tag="ps_os_text", color=themes.INFO)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            dpg.add_text("", tag="ps_mac_text", color=themes.TEXT_SECONDARY)

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=-24):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                with dpg.table(tag="ps_table", header_row=True, resizable=True,
                                borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                borders_outerV=True, scrollY=True, policy=dpg.mvTable_SizingStretchProp):
                    dpg.bind_item_theme("ps_table", "table_theme")
                    _add_table_columns()

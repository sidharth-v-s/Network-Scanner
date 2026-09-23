"""
quickrecon.py — Quick Recon screen.

A guided, one-click workflow: sweep a subnet for live hosts, then
automatically run a fast port scan against each host found, streaming
results into a single tree view (host -> open ports). This is the
"cool feature" combining the two most common first steps of an
external/internal recon phase into one action instead of two manual
tool switches.
"""

import threading

import dearpygui.dearpygui as dpg

import scan_engine
import scan_history
import themes
import ui_widgets

_cancel_token = scan_engine.ScanCancelToken()
_running = False


def _set_scanning_ui(is_scanning: bool):
    global _running
    _running = is_scanning
    dpg.configure_item("qr_start_btn", enabled=not is_scanning)
    dpg.configure_item("qr_stop_btn", show=is_scanning)


def _clear_tree():
    if dpg.does_item_exist("qr_tree"):
        dpg.delete_item("qr_tree", children_only=True)


def stop_scan():
    _cancel_token.cancel()
    ui_widgets.set_status("qr_status", "Stopping …", "warning")


def run_quick_recon():
    subnet = dpg.get_value("qr_input").strip()
    valid, err = scan_engine.validate_target(subnet)
    if not valid:
        ui_widgets.set_status("qr_status", err, "error")
        return

    _clear_tree()
    _cancel_token.reset()
    _set_scanning_ui(True)
    ui_widgets.set_status("qr_status", "Phase 1/2 — discovering live hosts …", "info")
    ui_widgets.set_progress("qr_progress", 0.0, "")

    def worker():
        # ---------------- Phase 1: host discovery ----------------
        def on_discovery_event(evt):
            if evt["kind"] == "error":
                ui_widgets.set_status("qr_status", evt["message"], "error")
            elif evt["kind"] == "status":
                ui_widgets.set_status("qr_status", evt["message"], "info")

        hosts = scan_engine.host_discovery(subnet, on_event=on_discovery_event,
                                            cancel_token=_cancel_token, resolve_hostnames=True)

        if _cancel_token.is_cancelled():
            ui_widgets.set_status("qr_status", "Cancelled during host discovery.", "warning")
            _set_scanning_ui(False)
            return

        if not hosts:
            ui_widgets.set_status("qr_status", "No live hosts found on that subnet.", "warning")
            ui_widgets.set_progress("qr_progress", 1.0, "")
            _set_scanning_ui(False)
            scan_history.add_entry("Quick Recon", subnet, "0 hosts found")
            return

        ui_widgets.set_status("qr_status", f"Phase 2/2 — scanning {len(hosts)} host(s) for open ports …", "info")

        total_open = 0
        for i, host in enumerate(hosts):
            if _cancel_token.is_cancelled():
                break

            node_tag = f"qr_node_{host.ip.replace('.', '_')}"
            label = f"{host.ip}"
            if host.hostname:
                label += f"  ({host.hostname})"
            if host.vendor:
                label += f"  [{host.vendor}]"

            with dpg.tree_node(label=label, tag=node_tag, parent="qr_tree", default_open=True):
                dpg.add_text("Scanning…", color=themes.TEXT_DISABLED, tag=f"{node_tag}_placeholder")

            def on_port_event(evt, node_tag=node_tag):
                if evt["kind"] == "port_found" and evt["port"].state == "open":
                    p = evt["port"]
                    if dpg.does_item_exist(f"{node_tag}_placeholder"):
                        dpg.delete_item(f"{node_tag}_placeholder")
                    color = themes.SEVERITY_COLORS.get(p.state, themes.TEXT_PRIMARY)
                    dpg.add_text(f"{p.port}/{p.protocol}  {p.state}  {p.display_service}",
                                 color=color, parent=node_tag)

            result = scan_engine.port_scan(
                host.ip, on_event=on_port_event, cancel_token=_cancel_token,
                scan_arguments="-T4 --top-ports 100",
            )
            open_ports = [p for p in result.ports if p.state == "open"]
            total_open += len(open_ports)

            if dpg.does_item_exist(f"{node_tag}_placeholder"):
                dpg.set_value(f"{node_tag}_placeholder", "No open ports in top 100.")
                dpg.configure_item(f"{node_tag}_placeholder", color=themes.TEXT_DISABLED)

            frac = (i + 1) / len(hosts)
            ui_widgets.set_progress("qr_progress", frac, f"{i + 1}/{len(hosts)} hosts")

        if _cancel_token.is_cancelled():
            ui_widgets.set_status("qr_status", f"Cancelled — {total_open} open port(s) found so far.", "warning")
        else:
            ui_widgets.set_status(
                "qr_status",
                f"Done — {len(hosts)} host(s), {total_open} open port(s) total.", "success",
            )
            ui_widgets.set_progress("qr_progress", 1.0, "Complete")
            scan_history.add_entry("Quick Recon", subnet,
                                    f"{len(hosts)} hosts, {total_open} open ports")

        _set_scanning_ui(False)

    threading.Thread(target=worker, daemon=True).start()


def build(parent):
    import fontsetup
    with dpg.group(parent=parent):
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group():
                dpg.add_text("Quick Recon")
                dpg.bind_item_font(dpg.last_item(), fontsetup.get_font("subheading"))
                dpg.add_text("Discover live hosts on a subnet, then auto-scan each for open ports.",
                              color=themes.TEXT_SECONDARY)
        dpg.add_spacer(height=16)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=145):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                ui_widgets.labeled_input("Subnet / CIDR", "qr_input", hint="e.g. 192.168.1.0/24", width=320)
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    ui_widgets.primary_button("Start Quick Recon", tag="qr_start_btn",
                                               callback=run_quick_recon, width=200)
                    ui_widgets.danger_button("Stop", tag="qr_stop_btn", callback=stop_scan, width=100)
                    dpg.configure_item("qr_stop_btn", show=False)

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.group(width=-24):
                ui_widgets.status_pill("qr_status", "Idle — enter a subnet to begin.")
                dpg.add_spacer(height=4)
                ui_widgets.progress("qr_progress")

        dpg.add_spacer(height=12)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=24)
            with dpg.child_window(width=-24, height=-24):
                dpg.bind_item_theme(dpg.last_item(), "card_theme")
                dpg.add_text("Results (by host)", color=themes.TEXT_SECONDARY)
                dpg.add_separator()
                with dpg.child_window(tag="qr_tree", border=False):
                    pass

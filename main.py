"""
main.py — Application entrypoint.

Network Security Scanner v3
A DearPyGui recon toolkit: host discovery, port scanning (with NSE
scripts), web directory brute-forcing, a chained "Quick Recon" workflow,
and local scan history — for use on systems you own or are authorized
to test.
"""

import os
import sys

import dearpygui.dearpygui as dpg

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app_shell
import fontsetup
import hostlookup
import portscanner
import webdir
import quickrecon
import history_view
import themes


def register_screens():
    app_shell.register_screen("Dashboard", "[*]", app_shell.build_dashboard)
    app_shell.register_screen("Host Discovery", "[NET]", hostlookup.build)
    app_shell.register_screen("Port Scanner", "[SCAN]", portscanner.build)
    app_shell.register_screen("Web Directory Scan", "[WEB]", webdir.build)
    app_shell.register_screen("Quick Recon", "[FAST]", quickrecon.build)
    app_shell.register_screen("Scan History", "[LOG]", history_view.build)


def main():
    dpg.create_context()
    dpg.create_viewport(title="Network Security Scanner", width=1180, height=760,
                         min_width=900, min_height=600)
    dpg.setup_dearpygui()
    dpg.set_viewport_clear_color(themes.BG_DARKEST)

    themes.create_themes()
    dpg.bind_font(fontsetup.get_font("body"))

    register_screens()
    app_shell.build_shell()

    dpg.set_viewport_resize_callback(lambda: app_shell.resize_shell())

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()

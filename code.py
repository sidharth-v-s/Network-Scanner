"""
code.py — Backwards-compatible string-based wrappers around scan_engine.

Kept so any external scripts importing `nmap_scan`, `port_scanner`, or
`find_subdirectories` (the original v2 API) keep working. New code should
use `scan_engine` directly for structured results.
"""

from scan_engine import (
    host_discovery,
    port_scan,
    web_directory_scan,
)


def nmap_scan(subnet, callback=None):
    lines = [f"Starting host lookup on subnet: {subnet}"]
    if callback:
        callback("\n".join(lines))

    def on_event(evt):
        if evt["kind"] == "error":
            lines.append(f"Error: {evt['message']}")
        elif evt["kind"] == "host_found":
            h = evt["host"]
            line = f"IP: {h.ip}"
            if h.hostname:
                line += f", Hostname: {h.hostname}"
            if h.mac:
                line += f", MAC: {h.mac}"
            if h.vendor:
                line += f", Vendor: {h.vendor}"
            lines.append(line)
        if callback:
            callback("\n".join(lines))

    results = host_discovery(subnet, on_event=on_event)
    if not results:
        lines.append("No hosts found.")
        if callback:
            callback("\n".join(lines))
    return lines


def port_scanner(port_ip, callback=None, scan_type="-A -T4"):
    lines = [f"Starting port scan on IP: {port_ip}", f"Scan type: {scan_type}"]
    if callback:
        callback("\n".join(lines))

    def on_event(evt):
        if evt["kind"] == "error":
            lines.append(f"Error: {evt['message']}")
            if callback:
                callback("\n".join(lines))

    result = port_scan(port_ip, on_event=on_event, scan_arguments=scan_type)
    if result.error:
        return lines

    for p in result.ports:
        lines.append(f"Port {p.port}/{p.protocol}: {p.state}, Service: {p.display_service}")
    for os_match in result.os_matches:
        lines.append(f"OS: {os_match['name']} (Accuracy: {os_match['accuracy']}%)")
    if result.mac:
        lines.append(f"MAC Address: {result.mac}")
    if result.vendor:
        lines.append(f"Hardware Vendor: {result.vendor}")

    if callback:
        callback("\n".join(lines))
    return lines


def find_subdirectories(url, wordlist_file, callback=None, stopInstance=None):
    lines = [f"Starting directory scan on: {url}"]
    if callback:
        callback("\n".join(lines))

    class _TokenAdapter:
        def is_cancelled(self_inner):
            return stopInstance is not None and not stopInstance.scan

    def on_event(evt):
        if evt["kind"] == "error":
            lines.append(f"Error: {evt['message']}")
        elif evt["kind"] == "dir_found":
            d = evt["result"]
            extra = f"     [Redirect to {d.redirect_to}]" if d.redirect_to else ""
            lines.append(f"Found: {d.url}     [Status: {d.status}]{extra}")
        if callback:
            callback("\n".join(lines))

    results = web_directory_scan(
        url, wordlist_file, on_event=on_event,
        cancel_token=_TokenAdapter() if stopInstance else None,
    )
    lines.append(f"\nScan complete. Found {len(results)} directories.")
    if callback:
        callback("\n".join(lines))
    return lines


if __name__ == "__main__":
    print("Network Security Scanner — CLI mode")
    while True:
        print("\nSelect a tool:")
        print("1. Host Lookup")
        print("2. Port Scanner")
        print("3. Subdirectory Scanner")
        print("4. Exit")

        choice = input("Enter choice (1/2/3/4): ")

        if choice == "1":
            subnet = input("Enter IP Subnet (e.g., 192.168.1.0/24): ")
            print("\n".join(nmap_scan(subnet)))
        elif choice == "2":
            port_ip = input("Enter IP Address for Port Scan: ")
            print("\n".join(port_scanner(port_ip)))
        elif choice == "3":
            url = input("Enter the base URL (e.g., https://example.com): ")
            wordlist_file = input("Enter the path to your wordlist file: ")
            print("\n".join(find_subdirectories(url, wordlist_file)))
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

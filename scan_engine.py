"""
scan_engine.py — Core scanning logic for Network Security Scanner.

This module is UI-agnostic: it knows nothing about DearPyGui. Every scan
function accepts an optional `on_event(event: dict)` callback so a caller
(GUI or CLI) can render progress however it likes, and an optional
`cancel_token` (a `ScanCancelToken`) so long scans can be stopped cleanly.

Design goals over the original implementation:
  - Input validation (CIDR / host / URL) before ever shelling out to nmap.
  - Clear, actionable errors (e.g. "nmap not found" instead of a raw
    traceback string dumped into a text box).
  - Structured results (lists of dicts) so the UI can render tables,
    filter, sort, and export — not just append to a giant log string.
  - Real cancellation for every scan type, not just the web scanner.
  - Concurrency for the web directory scanner (was fully serial).
  - Nmap Scripting Engine (NSE) helpers for common recon scripts.
"""

from __future__ import annotations

import concurrent.futures
import ipaddress
import json
import re
import shutil
import socket
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Optional
from urllib.parse import urlparse

try:
    import nmap
except ImportError:  # pragma: no cover - surfaced to the UI instead
    nmap = None

import requests

EventCallback = Optional[Callable[[dict], None]]


# ---------------------------------------------------------------------------
# Cancellation
# ---------------------------------------------------------------------------

class ScanCancelToken:
    """A simple thread-safe flag that scans poll periodically."""

    def __init__(self):
        self._cancelled = threading.Event()

    def cancel(self):
        self._cancelled.set()

    def is_cancelled(self) -> bool:
        return self._cancelled.is_set()

    def reset(self):
        self._cancelled.clear()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)


def validate_target(target: str) -> tuple[bool, str]:
    """Validate a single host / IP / CIDR / small range for scanning.

    Returns (is_valid, error_message). error_message is '' when valid.
    Accepts: single IP, CIDR ("10.0.0.0/24"), nmap-style short range
    ("10.0.0.1-50"), or a resolvable hostname.
    """
    target = (target or "").strip()
    if not target:
        return False, "Target cannot be empty."

    # CIDR
    if "/" in target:
        try:
            ipaddress.ip_network(target, strict=False)
            return True, ""
        except ValueError as e:
            return False, f"Invalid CIDR notation: {e}"

    # nmap short range like 10.0.0.1-50 or 10.0.0-1.1-50
    if "-" in target:
        base = target.split("-")[0]
        try:
            ipaddress.ip_address(base)
            return True, ""
        except ValueError:
            return False, "Invalid IP range format. Example: 192.168.1.1-50"

    # Plain IP
    try:
        ipaddress.ip_address(target)
        return True, ""
    except ValueError:
        pass

    # Reject dotted-quad-looking strings that failed ip_address() above
    # (e.g. "999.999.999.999") instead of falling through to the hostname
    # regex, which would otherwise accept them as a "domain".
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", target):
        return False, "Invalid IP address."

    # Hostname
    if _HOSTNAME_RE.match(target):
        return True, ""

    return False, "Enter a valid IP, CIDR (e.g. 192.168.1.0/24), range, or hostname."


def validate_url(url: str) -> tuple[bool, str, str]:
    """Validate a URL for the web directory scanner.

    Returns (is_valid, error_message, normalized_url).
    """
    url = (url or "").strip()
    if not url:
        return False, "URL cannot be empty.", ""

    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "http://" + url

    parsed = urlparse(url)
    if not parsed.netloc:
        return False, "That doesn't look like a valid URL.", ""

    if not url.endswith("/"):
        url += "/"

    return True, "", url


def nmap_available() -> tuple[bool, str]:
    """Check whether the nmap binary and python-nmap module are usable."""
    if nmap is None:
        return False, "python-nmap is not installed. Run: pip install python-nmap"
    if shutil.which("nmap") is None:
        return False, (
            "The 'nmap' binary was not found on your system PATH. "
            "Install it from https://nmap.org/download.html"
        )
    return True, ""


# ---------------------------------------------------------------------------
# Result data classes
# ---------------------------------------------------------------------------

@dataclass
class HostResult:
    ip: str
    hostname: str = ""
    mac: str = ""
    vendor: str = ""
    state: str = "up"


@dataclass
class PortResult:
    port: int
    protocol: str
    state: str
    service: str = ""
    product: str = ""
    version: str = ""
    extrainfo: str = ""

    @property
    def display_service(self) -> str:
        parts = [p for p in (self.product, self.version) if p]
        suffix = f" {' '.join(parts)}" if parts else ""
        extra = f" ({self.extrainfo})" if self.extrainfo else ""
        return f"{self.service}{suffix}{extra}"


@dataclass
class PortScanResult:
    target: str
    ports: List[PortResult] = field(default_factory=list)
    os_matches: List[dict] = field(default_factory=list)
    mac: str = ""
    vendor: str = ""
    scripts: dict = field(default_factory=dict)  # port -> {script_id: output}
    elapsed: float = 0.0
    error: str = ""


@dataclass
class DirResult:
    url: str
    status: int
    redirect_to: str = ""


# ---------------------------------------------------------------------------
# Host discovery
# ---------------------------------------------------------------------------

def host_discovery(
    subnet: str,
    on_event: EventCallback = None,
    cancel_token: Optional[ScanCancelToken] = None,
    resolve_hostnames: bool = True,
) -> List[HostResult]:
    """Ping-sweep a subnet/CIDR/range and return discovered hosts."""

    def emit(kind, **kw):
        if on_event:
            on_event({"kind": kind, **kw})

    ok, err = nmap_available()
    if not ok:
        emit("error", message=err)
        return []

    valid, err = validate_target(subnet)
    if not valid:
        emit("error", message=err)
        return []

    emit("status", message=f"Starting host discovery on {subnet} …")
    start = time.time()
    results: List[HostResult] = []

    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=subnet, arguments="-sn --max-retries 1 --host-timeout 15s")
    except Exception as e:  # noqa: BLE001 - surfaced verbatim to the user
        emit("error", message=f"nmap error: {e}")
        return []

    if cancel_token and cancel_token.is_cancelled():
        emit("cancelled")
        return results

    up_hosts = [h for h in nm.all_hosts() if nm[h].state() == "up"]
    emit("status", message=f"Found {len(up_hosts)} live host(s). Resolving details …")

    for i, host in enumerate(up_hosts):
        if cancel_token and cancel_token.is_cancelled():
            emit("cancelled")
            break

        hr = HostResult(ip=host)
        info = nm[host]

        hostnames = info.get("hostnames") or []
        if hostnames and hostnames[0].get("name"):
            hr.hostname = hostnames[0]["name"]
        elif resolve_hostnames:
            try:
                hr.hostname = socket.getfqdn(host)
                if hr.hostname == host:
                    hr.hostname = ""
            except Exception:  # noqa: BLE001
                pass

        addresses = info.get("addresses", {})
        if "mac" in addresses:
            hr.mac = addresses["mac"]
            vendor_map = info.get("vendor", {})
            if hr.mac in vendor_map:
                hr.vendor = vendor_map[hr.mac]

        results.append(hr)
        emit("host_found", host=hr, index=i + 1, total=len(up_hosts))

    elapsed = time.time() - start
    emit("complete", results=results, elapsed=elapsed)
    return results


# ---------------------------------------------------------------------------
# Port scanning
# ---------------------------------------------------------------------------

SCAN_PROFILES = {
    "Quick (top 100 ports)": "-T4 --top-ports 100",
    "Basic SYN Scan": "-sS -T4",
    "Version Detection": "-sV -T4",
    "OS Detection": "-O -T4",
    "Comprehensive (-A)": "-A -T4",
    "Fast Scan": "-F -T4",
    "UDP Scan": "-sU -T4 --top-ports 50",
    "All 65535 Ports": "-p- -T4",
    "Stealth + Version": "-sS -sV -T4",
    "Vulnerability Scan (NSE)": "-sV -T4 --script vuln",
}

# Curated NSE scripts useful for red team recon, grouped by purpose.
NSE_SCRIPT_GROUPS = {
    "Discovery": ["banner", "http-title", "ssl-cert", "smb-os-discovery"],
    "Enumeration": ["http-enum", "smb-enum-shares", "smb-enum-users", "ftp-anon"],
    "Vulnerability": ["vuln", "smb-vuln-ms17-010", "ssl-heartbleed", "http-vuln*"],
    "Auth / Brute": ["ssh-auth-methods", "ftp-anon", "mysql-empty-password"],
}


def build_nse_arguments(base_args: str, scripts: List[str]) -> str:
    if not scripts:
        return base_args
    script_arg = ",".join(scripts)
    return f"{base_args} --script {script_arg}"


def port_scan(
    target: str,
    on_event: EventCallback = None,
    cancel_token: Optional[ScanCancelToken] = None,
    scan_arguments: str = "-A -T4",
) -> PortScanResult:
    """Run an nmap scan against a single target with the given arguments."""

    def emit(kind, **kw):
        if on_event:
            on_event({"kind": kind, **kw})

    result = PortScanResult(target=target)

    ok, err = nmap_available()
    if not ok:
        result.error = err
        emit("error", message=err)
        return result

    valid, verr = validate_target(target)
    if not valid:
        result.error = verr
        emit("error", message=verr)
        return result

    emit("status", message=f"Starting scan on {target} ({scan_arguments}) …")
    start = time.time()

    try:
        np = nmap.PortScanner()
        np.scan(target, arguments=scan_arguments)
    except Exception as e:  # noqa: BLE001
        result.error = f"nmap error: {e}"
        emit("error", message=result.error)
        return result

    if cancel_token and cancel_token.is_cancelled():
        emit("cancelled")
        return result

    if target not in np.all_hosts():
        # nmap may have resolved to a different key (e.g. hostname vs ip)
        hosts = np.all_hosts()
        if not hosts:
            result.error = f"No response from {target}. Host may be down, firewalled, or blocking scans."
            emit("error", message=result.error)
            return result
        resolved = hosts[0]
    else:
        resolved = target

    info = np[resolved]

    for proto in info.all_protocols():
        for port in sorted(info[proto].keys()):
            pdata = info[proto][port]
            pr = PortResult(
                port=port,
                protocol=proto,
                state=pdata.get("state", "unknown"),
                service=pdata.get("name", "unknown"),
                product=pdata.get("product", ""),
                version=pdata.get("version", ""),
                extrainfo=pdata.get("extrainfo", ""),
            )
            result.ports.append(pr)
            if pr.state == "open":
                emit("port_found", port=pr)

            script_out = pdata.get("script")
            if script_out:
                result.scripts[f"{port}/{proto}"] = script_out

    if "osmatch" in info and info["osmatch"]:
        result.os_matches = [
            {"name": m["name"], "accuracy": m["accuracy"]} for m in info["osmatch"][:3]
        ]

    addresses = info.get("addresses", {})
    if "mac" in addresses:
        result.mac = addresses["mac"]
        vendor_map = info.get("vendor", {})
        if result.mac in vendor_map:
            result.vendor = vendor_map[result.mac]

    result.elapsed = time.time() - start
    emit("complete", results=result, elapsed=result.elapsed)
    return result


# ---------------------------------------------------------------------------
# Web directory / file brute-forcing
# ---------------------------------------------------------------------------

INTERESTING_STATUSES = {200, 201, 204, 301, 302, 307, 308, 401, 403, 500}


def _read_wordlist(path: str) -> List[str]:
    for encoding in ("utf-8", "ISO-8859-1"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return [line.strip() for line in f if line.strip()]
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("wordlist", b"", 0, 1, "unreadable encoding")


def web_directory_scan(
    url: str,
    wordlist_file: str,
    on_event: EventCallback = None,
    cancel_token: Optional[ScanCancelToken] = None,
    extensions: Optional[List[str]] = None,
    threads: int = 20,
    timeout: float = 6.0,
) -> List[DirResult]:
    """Brute-force directories/files on a web server, concurrently."""

    def emit(kind, **kw):
        if on_event:
            on_event({"kind": kind, **kw})

    valid, err, url = validate_url(url)
    if not valid:
        emit("error", message=err)
        return []

    try:
        subdirs = _read_wordlist(wordlist_file)
    except FileNotFoundError:
        emit("error", message=f"Wordlist not found: {wordlist_file}")
        return []
    except UnicodeDecodeError:
        emit("error", message=f"Could not decode wordlist: {wordlist_file}")
        return []

    if not subdirs:
        emit("error", message="Wordlist is empty.")
        return []

    extensions = extensions or [""]
    candidates = []
    for word in subdirs:
        for ext in extensions:
            candidates.append(word + ext if not word.endswith(ext) else word)
    # de-dup while preserving order
    seen = set()
    candidates = [c for c in candidates if not (c in seen or seen.add(c))]

    total = len(candidates)
    emit("status", message=f"Scanning {url} with {total} candidate paths ({threads} threads) …")

    results: List[DirResult] = []
    results_lock = threading.Lock()
    completed = 0
    completed_lock = threading.Lock()

    session = requests.Session()
    session.headers.update({"User-Agent": "NetworkSecurityScanner/2.0 (authorized-testing)"})

    def check_one(path_suffix: str):
        nonlocal completed
        if cancel_token and cancel_token.is_cancelled():
            return
        full_url = f"{url}{path_suffix}"
        try:
            resp = session.get(full_url, timeout=timeout, allow_redirects=False)
            if resp.status_code in INTERESTING_STATUSES:
                dr = DirResult(
                    url=full_url,
                    status=resp.status_code,
                    redirect_to=resp.headers.get("Location", "") if 300 <= resp.status_code < 400 else "",
                )
                with results_lock:
                    results.append(dr)
                emit("dir_found", result=dr)
        except requests.RequestException:
            pass
        finally:
            with completed_lock:
                completed += 1
                if completed % 10 == 0 or completed == total:
                    emit("progress", completed=completed, total=total)

    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_one, c) for c in candidates]
        for _ in concurrent.futures.as_completed(futures):
            if cancel_token and cancel_token.is_cancelled():
                break

    elapsed = time.time() - start

    if cancel_token and cancel_token.is_cancelled():
        emit("cancelled", results=results)
    else:
        emit("complete", results=results, elapsed=elapsed)

    return results


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def export_results(kind: str, data, path: str) -> None:
    """Write scan results to disk as .txt, .json, or .csv based on extension."""
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else "txt"

    if ext == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_to_serializable(data), f, indent=2, default=str)
        return

    if ext == "csv":
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if kind == "hosts":
                writer.writerow(["IP", "Hostname", "MAC", "Vendor"])
                for h in data:
                    writer.writerow([h.ip, h.hostname, h.mac, h.vendor])
            elif kind == "ports":
                writer.writerow(["Port", "Protocol", "State", "Service", "Product", "Version"])
                for p in data:
                    writer.writerow([p.port, p.protocol, p.state, p.service, p.product, p.version])
            elif kind == "dirs":
                writer.writerow(["URL", "Status", "Redirect"])
                for d in data:
                    writer.writerow([d.url, d.status, d.redirect_to])
        return

    # Plain text fallback
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Network Security Scanner export — {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        if kind == "hosts":
            for h in data:
                line = f"IP: {h.ip}"
                if h.hostname:
                    line += f"  Hostname: {h.hostname}"
                if h.mac:
                    line += f"  MAC: {h.mac}"
                if h.vendor:
                    line += f"  Vendor: {h.vendor}"
                f.write(line + "\n")
        elif kind == "ports":
            for p in data:
                f.write(f"{p.port}/{p.protocol}  {p.state}  {p.display_service}\n")
        elif kind == "dirs":
            for d in data:
                extra = f" -> {d.redirect_to}" if d.redirect_to else ""
                f.write(f"[{d.status}] {d.url}{extra}\n")


def _to_serializable(data):
    if isinstance(data, list):
        return [_to_serializable(x) for x in data]
    if hasattr(data, "__dict__"):
        return data.__dict__
    return data

import nmap
import requests
import concurrent.futures
from tkinter import Tk, filedialog
from time import sleep

def nmap_scan(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-sn')
    
    up_hosts = []
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            up_hosts.append(host)
    return up_hosts

def port_scanner(port_ip):
    np = nmap.PortScanner()
    np.scan(port_ip, arguments='-sV -p 80,20,21,22,23,25,53,110,443 -O -A -T5')
    port_results = []
    for proto in np[port_ip].all_protocols():
        lport = np[port_ip][proto].keys()
        for port in lport:
            if np[port_ip][proto][port]['state'] == 'open':
                port_info = {
                    'port': port,
                    'service': np[port_ip][proto][port]['name'],
                    'version': np[port_ip][proto][port].get('version', 'unknown')
                }
                port_results.append(port_info)
    if 'osmatch' in np[port_ip]:
        os_info = np[port_ip]['osmatch'][0]['name'] if np[port_ip]['osmatch'] else "Unknown"
        port_results.append({'os': os_info})
    return port_results

def check_subdirectory(url, subdirectory):
    full_url = f"{url}/{subdirectory}"
    try:
        response = requests.get(full_url, timeout=5)  # Set a timeout of 5 seconds
        if response.status_code == 200:
            print(f"[+] Found: {full_url}")
        else:
            print(f"[-] {full_url} - {response.status_code}")
    except requests.RequestException as e:
        print(f"[-] Error: {full_url} - {str(e)}")

def load_wordlist():
    root = Tk()
    root.withdraw()  # Hide the root window
    filepath = filedialog.askopenfilename()
    root.destroy()  # Destroy the root window after file selection
    
    if filepath:
        try:
            with open(filepath, 'r') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"[-] Wordlist file not found: {filepath}")
            return []
    else:
        print("[-] No file selected.")
        return []

if __name__ == "__main__":
    choice = int(input("""Enter your choice:
             1) Host Lookup
             2) Port Scanner
             3) Subdirectory Scanner
            """))
    
    if choice == 1:
        subnet = input("Enter the IP subnet (e.g., 192.168.1.0/24): ")
        up_hosts = nmap_scan(subnet)
        print("Hosts UP:")
        for host in up_hosts:
            print(host)

    elif choice == 2:
        port_ip = input("Enter the IP Address you want to scan: ")
        port_results = port_scanner(port_ip)
        for result in port_results:
            if 'port' in result:
                print(f"Port {result['port']} is open, Service: {result['service']}, Version: {result['version']}")
            elif 'os' in result:
                print(f"OS: {result['os']}")
        if not port_results:
            print("No open ports found or scan failed.")

    elif choice == 3:
        url = input("Enter target URL (e.g., http://example.com): ").strip()
        subdirectories = load_wordlist()
        if subdirectories:
            print(f"Starting subdirectory scan on {url}...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(check_subdirectory, url, subdirectory) for subdirectory in subdirectories]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()  # This will raise any exceptions that occurred during execution
                    except Exception as e:
                        print(f"[-] Thread encountered an error: {str(e)}")
            print("Subdirectory scan completed.")
        else:
            print("No subdirectories to scan.")

    else:
        print("Invalid choice!")

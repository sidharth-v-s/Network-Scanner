import nmap
import requests
import concurrent.futures

# Subdirectory Scanner Function
def find_subdirectories(url, wordlist_file):
    # Ensure the URL format ends with a '/'
    if not url.endswith('/'):
        url += '/'
    
    # Read the wordlist file with the appropriate encoding
    try:
        with open(wordlist_file, 'r', encoding='ISO-8859-1') as file:
            subdirs = file.read().splitlines()
    except FileNotFoundError:
        print(f"Error: The file '{wordlist_file}' was not found.")
        return
    except UnicodeDecodeError:
        print(f"Error: The file '{wordlist_file}' contains invalid characters for UTF-8 decoding.")
        return

    print(f"Starting directory scan on: {url}\n")

    # Check each subdirectory in the wordlist
    for subdir in subdirs:
        full_url = f"{url}{subdir}"
        try:
            response = requests.get(full_url)
            # If response code is 200, directory likely exists
            if response.status_code == 200:
                print(f"Found: {full_url}")
        except requests.RequestException as e:
            print(f"Error reaching {full_url}: {e}")


# Host Lookup Function
def nmap_scan(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-sn')
    up_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']
    return up_hosts

def start_host_lookup(subnet):
    print(f"Starting host lookup on subnet: {subnet}")
    try:
        up_hosts = nmap_scan(subnet)
        if up_hosts:
            print("Hosts found:")
            for host in up_hosts:
                print(host)
        else:
            print("No hosts found.")
    except Exception as e:
        print(f"Error during host lookup: {str(e)}")

# Port Scanner Function
def port_scanner(port_ip):
    np = nmap.PortScanner()
    np.scan(port_ip, arguments='-sV -p 80,20,21,22,23,25,53,110,443,66,8000 -O -A -T5')
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

def start_port_scan(port_ip):
    print(f"Starting port scan on IP: {port_ip}")
    try:
        port_results = port_scanner(port_ip)
        if port_results:
            for result in port_results:
                if 'port' in result:
                    print(f"Port {result['port']} is open, Service: {result['service']}, Version: {result['version']}")
                elif 'os' in result:
                    print(f"OS: {result['os']}")
        else:
            print("No open ports found or scan failed.")
    except Exception as e:
        print(f"Error during port scan: {str(e)}")

if __name__ == "__main__":
    print("Cybersecurity Tools")

    while True:
        print("\nSelect a tool:")
        print("1. Host Lookup")
        print("2. Port Scanner")
        print("3. Subdirectory Scanner")
        print("4. Exit")

        choice = input("Enter choice (1/2/3/4): ")

        if choice == "1":
            subnet = input("Enter IP Subnet (e.g., 192.168.1.0/24): ")
            start_host_lookup(subnet)

        elif choice == "2":
            port_ip = input("Enter IP Address for Port Scan: ")
            start_port_scan(port_ip)

        elif choice == "3":
            url = input("Enter the base URL (e.g., https://example.com): ")
            wordlist_file = input("Enter the path to your wordlist file: ")
            find_subdirectories(url, wordlist_file)

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

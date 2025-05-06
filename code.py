import nmap
import requests
import concurrent.futures
import threading

# Subdirectory Scanner Function
def find_subdirectories(url, wordlist_file, callback=None,stopInstance = None):
    results = []
    
    # Ensure the URL format ends with a '/'
    if not url.endswith('/'):
        url += '/'
    
    # Read the wordlist file with the appropriate encoding
    try:
        with open(wordlist_file, 'r', encoding='ISO-8859-1') as file:
            subdirs = file.read().splitlines()
    except FileNotFoundError:
        results.append(f"Error: The file '{wordlist_file}' was not found.")
        if callback:
            callback("\n".join(results))
        return results
    except UnicodeDecodeError:
        # Try with UTF-8 if ISO-8859-1 fails
        try:
            with open(wordlist_file, 'r', encoding='utf-8') as file:
                subdirs = file.read().splitlines()
        except UnicodeDecodeError:
            results.append(f"Error: The file '{wordlist_file}' contains invalid characters.")
            if callback:
                callback("\n".join(results))
            return results

    results.append(f"Starting directory scan on: {url}\n")
    if callback:
        callback("\n".join(results))

    # Check each subdirectory in the wordlist
    found_count = 0
    for subdir in subdirs:
        if not stopInstance.scan:
            print('end thred')
            break
        if not subdir.strip():  # Skip empty lines
            continue
            
        full_url = f"{url}{subdir}"
        try:
            response = requests.get(full_url, timeout=5)
            # If response code is 200, directory likely exists
            if response.status_code == 200:
                found_count += 1
                results.append(f"Found: {full_url}")
                if callback and found_count % 5 == 0:  # Update UI every 5 findings
                    callback("\n".join(results))
        except requests.RequestException as e:
            results.append(f"Error reaching {full_url}: {e}")
            if callback and found_count % 5 == 0:
                callback("\n".join(results))
    
    results.append(f"\nScan complete. Found {found_count} directories.")
    if callback:
        callback("\n".join(results))
    return results

# Host Lookup Function
def nmap_scan(subnet, callback=None):
    results = []
    results.append(f"Starting host lookup on subnet: {subnet}")
    if callback:
        callback("\n".join(results))
        
    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=subnet, arguments='-sn')
        up_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']
        
        if up_hosts:
            results.append("Hosts found:")
            for host in up_hosts:
                results.append(host)
        else:
            results.append("No hosts found.")
    except Exception as e:
        results.append(f"Error during host lookup: {str(e)}")
    
    if callback:
        callback("\n".join(results))
    return results

# Port Scanner Function
def port_scanner(port_ip, callback=None):
    results = []
    results.append(f"Starting port scan on IP: {port_ip}")
    if callback:
        callback("\n".join(results))
        
    try:
        np = nmap.PortScanner()
        np.scan(port_ip, arguments='-sV -p 80,20,21,22,23,25,53,110,443,66,8000 -T4')
        
        for proto in np[port_ip].all_protocols():
            lport = np[port_ip][proto].keys()
            for port in lport:
                if np[port_ip][proto][port]['state'] == 'open':
                    service = np[port_ip][proto][port]['name']
                    version = np[port_ip][proto][port].get('version', 'unknown')
                    results.append(f"Port {port} is open, Service: {service}, Version: {version}")
        
        # Try to get OS info if available
        try:
            if 'osmatch' in np[port_ip] and np[port_ip]['osmatch']:
                os_info = np[port_ip]['osmatch'][0]['name']
                results.append(f"OS: {os_info}")
        except:
            pass
            
        if len(results) == 1:  # Only the starting message
            results.append("No open ports found.")
            
    except Exception as e:
        results.append(f"Error during port scan: {str(e)}")
    
    if callback:
        callback("\n".join(results))
    return results

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
 # type: ignore
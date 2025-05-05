# Network Security Scanner

A Python-based network security toolkit with a modern GUI interface built using DearPyGui. This application provides essential security scanning tools to help security professionals, network administrators, and cybersecurity enthusiasts assess network vulnerabilities.

## Features

### 🔍 Host Discovery
- Scan local or remote networks for active hosts
- Supports subnet scanning with CIDR notation (e.g., 192.168.1.0/24)
- Fast, multi-threaded scanning capabilities

### 🔌 Port Scanner
- Identify open ports on target systems
- Service and version detection
- Operating system fingerprinting when possible
- Pre-configured for common ports (21, 22, 23, 25, 53, 66, 80, 110, 443, 8000)

### 🌐 Web Directory Scanner
- Discover hidden directories and files on web servers
- Customizable with your own wordlists
- Threaded scanning for improved performance
- Easy-to-read results display



## Installation

### Prerequisites
- Python 3.6+
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sidharth-v-s/Network-Scanner-Tool.git
   cd Network-Scanner-Tool
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

### Dependencies

- **DearPyGui**: For the modern GUI interface
- **python-nmap**: For network scanning capabilities
- **requests**: For HTTP requests and web directory scanning
- **concurrent.futures**: For multi-threading support
- **tkinter**: For file dialogs

## Usage

### Host Lookup
1. Select "Host Look Up" from the main menu
2. Enter the subnet to scan (e.g., 192.168.1.0/24)
3. Click "Scan" and wait for the results

### Port Scanner
1. Select "Port Scanner" from the main menu
2. Enter the IP address to scan
3. Click "Scan" to begin port scanning

### Web Directory Scanner
1. Select "Web Subdirectory Finder" from the main menu
2. Enter the target URL (e.g., https://example.com)
3. Browse and select a wordlist file
4. Click "Scan" to begin the directory scan

## Customization

### Adding Custom Wordlists
You can use any text file as a wordlist for the Web Directory Scanner. Each line in the file should contain a directory or file name to check on the target website.

### Modifying Scanned Ports
To modify which ports are scanned, edit the `port_scanner` function in `code.py` and update the port list in the `np.scan()` function call.

## Security and Legal Considerations

⚠️ **Important Notice**

This tool is intended for authorized security testing, educational purposes, and system administrators managing their own networks. Using this tool against systems without explicit permission is illegal in many jurisdictions and violates computer fraud and abuse laws.

- **Always obtain written permission** before scanning any systems you don't own
- Use only on your own networks or with explicit authorization
- The developers assume no liability for misuse of this software

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the DearPyGui team for the excellent GUI framework
- Inspired by various open-source security tools

---

⭐ If you find this project useful, please consider giving it a star on GitHub!

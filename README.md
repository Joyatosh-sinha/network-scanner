# Network Scanner

A Python-based network reconnaissance tool for host discovery, TCP port scanning, service identification, and basic banner grabbing.

## Features

- Host reachability checks using system ping.
- TCP port scanning over a configurable port range.
- Hostname-to-IP resolution.
- Basic service identification by port number.
- Banner grabbing for accessible services.
- Scan results saved to a text report.
- Input validation for port ranges.
- Unit tests using Python's built-in `unittest` framework.

## Project Structure

```text
network-scanner/
├── docs/
├── examples/
├── images/
├── results/
│   └── scan_results.txt
├── src/
│   ├── __init__.py
│   ├── scanner.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_scanner.py
│   └── test_utils.py
├── .gitignore
├── LICENSE
├── main.py
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.10 or newer
- Windows, Linux, or macOS

The scanner uses Python standard-library modules for its core functionality.

## Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/Joyatosh-sinha/network-scanner.git
cd network-scanner
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the scanner with the virtual environment's Python executable directly.

## Usage

Scan the first 100 TCP ports:

```bash
python main.py --target 127.0.0.1
```

Scan a specific port range:

```bash
python main.py --target 127.0.0.1 --start 7990 --end 8010
```

Scan a single local port:

```bash
python main.py --target 127.0.0.1 --start 8000 --end 8000
```

Run the unit tests:

```bash
python -m unittest discover -s tests -v
```

## Example Output

```text
NETWORK SCANNER
Target : 127.0.0.1
IP     : 127.0.0.1
Ports  : 8000-8000

[+] Host 127.0.0.1 is UP.
[+] Port 8000 is OPEN
[+] Scan completed.
```

Actual output may vary depending on the target and running services.

## Results

Scan reports are stored in the `results/` directory when report saving is enabled.

## Security and Ethical Use

Use this tool only on systems you own or have explicit authorization to test. Scan responsibly and comply with applicable laws and policies.

## Testing

The project includes unit tests for port-status handling, service-name lookup, and hostname resolution.

Run all tests using:

```bash
python -m unittest discover -s tests -v
```

## Author

**Joyatosh Sinha**

- GitHub: https://github.com/Joyatosh-sinha

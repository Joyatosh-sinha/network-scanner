
# Security Testing Guide

This guide explains how to use the Python Network Scanner for basic network reconnaissance, interpret scan results, and perform authorized security testing.

## 1. Purpose

The Network Scanner is an educational Python tool designed to identify open TCP ports on a target host.

It helps users understand:

- TCP port scanning.
- Network service identification.
- Basic banner grabbing.
- Concurrent network scanning.
- Scan result documentation.
- Responsible security testing.

**Important:** This project is a basic reconnaissance tool. It is not a vulnerability scanner and does not prove that a system is secure or insecure.

## 2. How TCP Port Scanning Works

Network services listen for incoming connections on specific TCP ports.

Examples include:

| Port | Common service |
|---|---|
| 21 | FTP |
| 22 | SSH |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 3306 | MySQL |
| 8000 | Development HTTP server |
| 8080 | Alternative HTTP |

The scanner attempts to establish a TCP connection to each requested port.

### Understanding scan results

- **Open:** A TCP connection was successfully established. A service may be listening.
- **Closed:** The connection attempt was refused, indicating that the host responded but no service accepted the connection.
- **Filtered or unreachable:** A firewall, network filter, routing issue, or other condition may prevent a reliable connection result.

This scanner currently reports open ports. A port not reported as open should not automatically be classified as closed.

## 3. Service Identification

After detecting an open port, the scanner attempts to identify its service.

It uses:

- Common port-to-service mappings.
- Basic banner inspection.
- Simple protocol signatures.

For selected HTTP ports, it sends an HTTP HEAD request and reads the response.

Example banner:

```text
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.14.6
```

Banner information can help identify the software responding to a connection.

However, banners can be hidden, modified, incomplete, or misleading. Service identification is therefore an estimate, not definitive proof of software identity or version.

## 4. Authorized Testing Environment

Only scan systems that you own or have explicit permission to test.

A safe way to experiment is to run a local HTTP server on your own computer.

### Terminal 1: Start a local server

```powershell
python -m http.server 8000
```

### Terminal 2: Run the scanner

From the project directory:

```powershell
python main.py --target 127.0.0.1 --start 7999 --end 8001 --workers 50
```

Expected result:

- Port 8000 should appear as open.
- The scanner may identify the service as HTTP.
- A response banner may be displayed.

Stop the local server with `Ctrl+C` when finished.

## 5. Exporting Scan Results

The scanner supports three report formats.

### Text report

```powershell
python main.py --target 127.0.0.1 --start 7999 --end 8001 --format txt
```

### CSV report

```powershell
python main.py --target 127.0.0.1 --start 7999 --end 8001 --format csv
```

### JSON report

```powershell
python main.py --target 127.0.0.1 --start 7999 --end 8001 --format json
```

Reports are saved in the `results/` directory.

Use CSV for spreadsheet analysis and JSON when integrating scan results into other scripts or tools.

## 6. Interpreting Findings

An open port is not automatically a vulnerability.

When reviewing results, consider:

1. Is the service expected to be accessible?
2. Is the service necessary for the system?
3. Is the service exposed beyond its intended network?
4. Is the software maintained and updated?
5. Does the service require authentication?
6. Are appropriate firewall rules in place?

Further investigation should use authorized tools and reliable vendor documentation.

## 7. Limitations

This project has several limitations:

- It performs TCP connection-based scanning only.
- It does not perform UDP scanning.
- It does not identify vulnerabilities or verify CVEs.
- Banner grabbing supports only basic protocol interactions.
- Service identification relies on simple signatures and common port mappings.
- Firewalls and network conditions can affect scan results.
- A successful connection does not establish that a service is vulnerable.

## 8. Responsible Security Practices

Follow these principles during testing:

- Obtain permission before scanning a system.
- Use a controlled lab whenever possible.
- Avoid disrupting production services.
- Use reasonable port ranges and worker counts.
- Do not attempt exploitation without explicit authorization.
- Protect scan reports because they may contain sensitive infrastructure information.
- Follow applicable laws and organizational security policies.

## 9. Learning Outcomes

Building and testing this project provides practical experience with:

- Python socket programming.
- TCP networking fundamentals.
- Concurrent programming.
- Basic service fingerprinting.
- Command-line application development.
- Automated testing with `unittest`.
- Code quality checks with Ruff.
- Continuous integration using GitHub Actions.
- Security documentation and responsible reconnaissance.

---

**Project:** Python Network Scanner  
**Author:** Joyatosh Sinha  
**GitHub:** https://github.com/Joyatosh-sinha/network-scanner

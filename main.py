from datetime import datetime
from pathlib import Path
import argparse

from src.scanner import (
    is_host_up,
    scan_port,
    get_service_name,
    grab_banner,
)
from src.utils import resolve_target


def save_results(target, ip_address, start_port, end_port, open_ports):
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    report_path = results_dir / "scan_results.txt"

    with report_path.open("a", encoding="utf-8") as file:
        file.write("\n" + "=" * 60 + "\n")
        file.write("NETWORK SCAN REPORT\n")
        file.write("=" * 60 + "\n")
        file.write(f"Date       : {datetime.now().astimezone()}\n")
        file.write(f"Target     : {target}\n")
        file.write(f"IP Address : {ip_address}\n")
        file.write(f"Port Range : {start_port}-{end_port}\n")
        file.write(f"Open Ports : {len(open_ports)}\n")
        file.write("-" * 60 + "\n")

        if open_ports:
            for result in open_ports:
                file.write(
                    f"Port {result['port']} | "
                    f"Service: {result['service'].upper()}\n"
                )

                if result["banner"]:
                    file.write(f"Banner: {result['banner']}\n")
        else:
            file.write("No open TCP ports found.\n")

        file.write("=" * 60 + "\n")

    print(f"[+] Report saved to: {report_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Network Scanner - Host discovery and TCP port scanning"
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Target hostname or IP address",
    )

    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting TCP port (default: 1)",
    )

    parser.add_argument(
        "--end",
        type=int,
        default=100,
        help="Ending TCP port (default: 100)",
    )

    args = parser.parse_args()

    # Validate port range
    if not 1 <= args.start <= 65535:
        parser.error("Start port must be between 1 and 65535.")

    if not 1 <= args.end <= 65535:
        parser.error("End port must be between 1 and 65535.")

    if args.start > args.end:
        parser.error("Start port cannot be greater than end port.")

    # Resolve target hostname or IP address
    try:
        ip_address = resolve_target(args.target)
    except (ValueError, OSError) as error:
        print(f"[!] Could not resolve target: {error}")
        return

    # Display scan information
    print("=" * 60)
    print("NETWORK SCANNER")
    print("=" * 60)
    print(f"Target : {args.target}")
    print(f"IP     : {ip_address}")
    print(f"Ports  : {args.start}-{args.end}")
    print("=" * 60)

    # Check host availability
    print(f"\n[*] Checking whether {ip_address} is reachable...")

    if not is_host_up(ip_address):
        print(
            f"[!] Host {ip_address} may be down "
            "or blocking ICMP."
        )
        print("[!] Continuing with TCP scanning anyway.")

    else:
        print(f"[+] Host {ip_address} responded to the check.")

    # Scan TCP ports
    print(
        f"\n[*] Scanning TCP ports "
        f"{args.start}-{args.end}..."
    )

    open_ports = []

    for port in range(args.start, args.end + 1):
        if not scan_port(ip_address, port):
            continue

        service = get_service_name(port)
        banner = grab_banner(ip_address, port)

        result = {
            "port": port,
            "service": service,
            "banner": banner,
        }

        open_ports.append(result)

        print(
            f"[+] Port {port} is OPEN | "
            f"Service: {service.upper()}"
        )

        if banner:
            print(f"    Banner: {banner}")

    # Display results
    print("\n" + "=" * 60)
    print("SCAN RESULTS")
    print("=" * 60)

    if open_ports:
        print(f"[+] Open ports found: {len(open_ports)}\n")

        for result in open_ports:
            print(
                f"Port {result['port']} | "
                f"Service: {result['service'].upper()}"
            )

            if result["banner"]:
                print(f"Banner: {result['banner']}")

    else:
        print("[-] No open TCP ports found.")

    print("=" * 60)
    print("[+] Scan completed.")
    save_results(
    args.target,
    ip_address,
    args.start,
    args.end,
    open_ports,
)


if __name__ == "__main__":
    main()

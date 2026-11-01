
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from src.scanner import (
    grab_banner,
    identify_service,
    is_host_up,
    scan_ports,
)
from src.utils import resolve_target


def create_report_data(
    target,
    ip_address,
    start_port,
    end_port,
    open_ports,
):
    """Create structured scan report data."""
    return {
        "scan_date": datetime.now().astimezone().isoformat(),
        "target": target,
        "ip_address": ip_address,
        "port_range": {
            "start": start_port,
            "end": end_port,
        },
        "total_open_ports": len(open_ports),
        "open_ports": open_ports,
    }


def save_text_report(report):
    """Save scan results to a human-readable text report."""
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    report_path = results_dir / "scan_results.txt"

    with report_path.open("a", encoding="utf-8") as file:
        file.write("\n" + "=" * 60 + "\n")
        file.write("NETWORK SCAN REPORT\n")
        file.write("=" * 60 + "\n")
        file.write(f"Date       : {report['scan_date']}\n")
        file.write(f"Target     : {report['target']}\n")
        file.write(f"IP Address : {report['ip_address']}\n")
        file.write(
            f"Port Range : {report['port_range']['start']}-"
            f"{report['port_range']['end']}\n"
        )
        file.write(
            f"Open Ports : {report['total_open_ports']}\n"
        )
        file.write("-" * 60 + "\n")

        if report["open_ports"]:
            for result in report["open_ports"]:
                file.write(
                    f"Port {result['port']} | "
                    f"Service: {result['service'].upper()}\n"
                )

                if result["banner"]:
                    file.write(f"Banner: {result['banner']}\n")
        else:
            file.write("No open TCP ports found.\n")

        file.write("=" * 60 + "\n")

    print(f"[+] Text report saved to: {report_path}")


def save_csv_report(report):
    """Save open-port results as a CSV report."""
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = results_dir / f"scan_results_{timestamp}.csv"

    fieldnames = [
        "scan_date",
        "target",
        "ip_address",
        "port",
        "service",
        "banner",
    ]

    with report_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in report["open_ports"]:
            writer.writerow({
                "scan_date": report["scan_date"],
                "target": report["target"],
                "ip_address": report["ip_address"],
                "port": result["port"],
                "service": result["service"],
                "banner": result["banner"],
            })

    print(f"[+] CSV report saved to: {report_path}")


def save_json_report(report):
    """Save complete scan results as a JSON report."""
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = results_dir / f"scan_results_{timestamp}.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print(f"[+] JSON report saved to: {report_path}")


def save_results(report, output_format):
    """Save scan results in the selected format."""
    if output_format == "txt":
        save_text_report(report)
    elif output_format == "csv":
        save_csv_report(report)
    elif output_format == "json":
        save_json_report(report)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


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

    parser.add_argument(
        "--workers",
        type=int,
        default=100,
        help="Number of concurrent scanning workers (default: 100)",
    )

    parser.add_argument(
        "--format",
        choices=["txt", "csv", "json"],
        default="txt",
        help="Report format: txt, csv, or json (default: txt)",
    )

    args = parser.parse_args()

    if not 1 <= args.start <= 65535:
        parser.error("Start port must be between 1 and 65535.")

    if not 1 <= args.end <= 65535:
        parser.error("End port must be between 1 and 65535.")

    if args.start > args.end:
        parser.error("Start port cannot be greater than end port.")

    if args.workers < 1:
        parser.error("Workers must be at least 1.")

    try:
        ip_address = resolve_target(args.target)
    except (ValueError, OSError) as error:
        print(f"[!] Could not resolve target: {error}")
        return

    print("=" * 60)
    print("NETWORK SCANNER")
    print("=" * 60)
    print(f"Target  : {args.target}")
    print(f"IP      : {ip_address}")
    print(f"Ports   : {args.start}-{args.end}")
    print(f"Workers : {args.workers}")
    print(f"Format  : {args.format.upper()}")
    print("=" * 60)

    print(f"\n[*] Checking whether {ip_address} is reachable...")

    if not is_host_up(ip_address):
        print(
            f"[!] Host {ip_address} may be down "
            "or blocking ICMP."
        )
        print("[!] Continuing with TCP scanning anyway.")
    else:
        print(f"[+] Host {ip_address} responded to the check.")

    print(
        f"\n[*] Scanning TCP ports "
        f"{args.start}-{args.end} using {args.workers} workers..."
    )

    open_port_numbers = scan_ports(
        ip_address,
        args.start,
        args.end,
        workers=args.workers,
    )

    open_ports = []

    for port in open_port_numbers:
        banner = grab_banner(ip_address, port)
        service = identify_service(port, banner)

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

    report = create_report_data(
        args.target,
        ip_address,
        args.start,
        args.end,
        open_ports,
    )

    save_results(report, args.format)


if __name__ == "__main__":
    main()

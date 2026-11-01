
import argparse
import time

from src.scanner import scan_port, scan_ports
from src.utils import resolve_target


def benchmark_scan(target, start_port, end_port, workers):
    """Compare sequential and concurrent TCP scanning."""

    ip_address = resolve_target(target)

    print("=" * 60)
    print("NETWORK SCANNER PERFORMANCE BENCHMARK")
    print("=" * 60)
    print(f"Target  : {target}")
    print(f"IP      : {ip_address}")
    print(f"Ports   : {start_port}-{end_port}")
    print(f"Workers : {workers}")
    print("=" * 60)

    # Sequential scan
    print("\n[*] Running sequential scan...")

    sequential_start = time.perf_counter()

    sequential_open = [
        port
        for port in range(start_port, end_port + 1)
        if scan_port(ip_address, port)
    ]

    sequential_time = time.perf_counter() - sequential_start

    # Concurrent scan
    print("[*] Running concurrent scan...")

    concurrent_start = time.perf_counter()

    concurrent_open = scan_ports(
        ip_address,
        start_port,
        end_port,
        workers=workers,
    )

    concurrent_time = time.perf_counter() - concurrent_start

    # Results
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)

    print(f"Sequential time : {sequential_time:.4f} seconds")
    print(f"Concurrent time : {concurrent_time:.4f} seconds")

    print(f"\nSequential open ports : {sequential_open}")
    print(f"Concurrent open ports : {concurrent_open}")

    if concurrent_time > 0:
        speedup = sequential_time / concurrent_time
        print(f"\nPerformance speedup : {speedup:.2f}x")

    if sequential_open == concurrent_open:
        print("[+] Both scanning methods returned matching results.")
    else:
        print("[!] Warning: Scan results differ between methods.")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark sequential and concurrent TCP scanning."
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
        help="Number of concurrent workers (default: 100)",
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
        benchmark_scan(
            args.target,
            args.start,
            args.end,
            args.workers,
        )
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

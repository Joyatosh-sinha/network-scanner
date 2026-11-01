
import platform
import socket
import subprocess


def _validate_port(port):
    """Ensure a TCP port is within the valid range."""
    if isinstance(port, bool) or not isinstance(port, int):
        raise TypeError("Port must be an integer.")

    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")


def _validate_timeout(timeout):
    """Ensure a timeout is a positive number."""
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise TypeError("Timeout must be a positive number.")

    if timeout <= 0:
        raise ValueError("Timeout must be greater than zero.")


def grab_banner(ip, port, timeout=2):
    """Attempt to grab a banner from an open TCP service."""
    _validate_port(port)
    _validate_timeout(timeout)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))

            if port in (80, 8000, 8080):
                request = b"HEAD / HTTP/1.0\r\nHost: localhost\r\n\r\n"
                sock.sendall(request)

            banner = sock.recv(1024)

            if not banner:
                return None

            return banner.decode("utf-8", errors="replace").strip() or None

    except OSError:
        return None


def scan_port(ip, port, timeout=1):
    """Check whether a TCP port is open."""
    _validate_port(port)
    _validate_timeout(timeout)

    sock = None

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        return sock.connect_ex((ip, port)) == 0

    except OSError:
        return False

    finally:
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass


def is_host_up(ip):
    """Check whether a host responds to an ICMP ping."""
    if not isinstance(ip, str) or not ip.strip():
        return False

    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", "1", "-w", "1000", ip]
    elif system in ("linux", "darwin"):
        command = ["ping", "-c", "1", "-W", "1", ip]
    else:
        return False

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=3,
        )

        return result.returncode == 0

    except (subprocess.SubprocessError, OSError):
        return False


def get_service_name(port):
    """Return a known TCP service name for a port."""
    if isinstance(port, bool) or not isinstance(port, int):
        return "unknown"

    if not 1 <= port <= 65535:
        return "unknown"

    common_services = {
        8000: "http-alt",
        8080: "http-proxy",
        8443: "https-alt",
    }

    if port in common_services:
        return common_services[port]

    try:
        return socket.getservbyport(port, "tcp")
    except (OSError, ValueError):
        return "unknown"


def identify_service(port, banner):
    """
    Identify a service using banner evidence.
    Fall back to the port-based service name when unknown.
    """
    if not banner:
        return get_service_name(port)

    banner_lower = banner.lower()

    if banner_lower.startswith("ssh-"):
        return "ssh"

    if "mysql" in banner_lower:
        return "mysql"

    if "postgresql" in banner_lower:
        return "postgresql"

    if banner_lower.startswith("http/"):
        return "http"

    if port == 21 and banner_lower.startswith(("220 ", "220-")):
        return "ftp"

    if port in (25, 587) and banner_lower.startswith(("220 ", "220-")):
        return "smtp"

    return get_service_name(port)

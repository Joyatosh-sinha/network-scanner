import socket
import subprocess
import platform

def grab_banner(ip, port, timeout=2):
    """
    Attempt to grab a banner from an open TCP service.
    """

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))

            # Send a simple HTTP request for HTTP-like ports
            if port in [80, 8000, 8080]:
                request = b"HEAD / HTTP/1.0\r\n\r\n"
                sock.sendall(request)

            banner = sock.recv(1024)

            return banner.decode(errors="ignore").strip()

    except (socket.error, UnicodeDecodeError):
        return None
    
def scan_port(ip, port, timeout=1):
    """
    Check whether a TCP port is open.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        result = sock.connect_ex((ip, port))
        return result == 0

    except socket.error:
        return False

    finally:
        sock.close()


def is_host_up(ip):
    """
    Check whether a host responds to an ICMP ping.
    """

    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", "1", "-w", "1000", ip]
    else:
        command = ["ping", "-c", "1", "-W", "1", ip]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return result.returncode == 0

    except (subprocess.SubprocessError, OSError):
        return False


def get_service_name(port):
    """
    Return the service name associated with a port.
    """

    try:
        return socket.getservbyport(port)
    except OSError:
        return "unknown"
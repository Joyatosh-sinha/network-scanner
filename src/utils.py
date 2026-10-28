
import socket


def resolve_target(target):
    """Resolve a hostname or validate an IP address."""
    try:
        return socket.gethostbyname(target)
    except (socket.gaierror, OSError) as error:
        raise ValueError(
            f"Unable to resolve target '{target}': {error}"
        ) from error

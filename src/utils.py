
import socket


def resolve_target(target):
    """
    Resolve a hostname or IP address to an IPv4 address.

    Raises:
        ValueError: If the target is empty or cannot be resolved.
    """
    if not isinstance(target, str) or not target.strip():
        raise ValueError("Target must be a non-empty hostname or IP address.")

    target = target.strip()

    try:
        return socket.gethostbyname(target)

    except (socket.gaierror, OSError) as error:
        raise ValueError(
            f"Unable to resolve target '{target}': {error}"
        ) from error

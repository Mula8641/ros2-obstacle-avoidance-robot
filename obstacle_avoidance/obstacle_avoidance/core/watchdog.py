from typing import Optional


def scan_is_stale(seconds_since_scan: Optional[float], timeout_s: float) -> bool:
    """True when no scan has ever arrived (None) or the last one is older than timeout_s."""
    return seconds_since_scan is None or seconds_since_scan > timeout_s

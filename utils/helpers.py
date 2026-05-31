import datetime


def format_size(size_bytes: int) -> str:
    """Return a human-readable file size string."""
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} Ko"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} Mo"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} Go"


def format_date(timestamp: float) -> str:
    """Return a human-readable modification date string."""
    if not timestamp:
        return "—"
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%d/%m/%Y %H:%M")


def truncate_path(path: str, max_length: int = 60) -> str:
    """Truncate a path string for display purposes."""
    if len(path) <= max_length:
        return path
    return "…" + path[-(max_length - 1):]
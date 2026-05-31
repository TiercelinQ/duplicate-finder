from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileEntry:
    """Represents a single file with its metadata and computed identifiers."""

    path: Path
    name: str = field(init=False)
    size: int = 0
    modified: float = 0.0
    sha256: str = ""
    group_key: str = ""

    def __post_init__(self) -> None:
        self.name = self.path.name

    @property
    def size_display(self) -> str:
        """Human-readable file size."""
        from utils.helpers import format_size
        return format_size(self.size)

    @property
    def modified_display(self) -> str:
        """Human-readable modification date."""
        from utils.helpers import format_date
        return format_date(self.modified)

    @property
    def path_display(self) -> str:
        """String representation of the file path."""
        return str(self.path)
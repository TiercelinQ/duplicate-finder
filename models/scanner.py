import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from config import HASH_CHUNK_SIZE, ScanMode
from models.file_entry import FileEntry


class ScanWorker(QThread):
    """Performs duplicate file scanning in a background thread."""

    progress = pyqtSignal(int, int)
    file_scanned = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(
        self,
        folders: list[Path],
        recursive: bool,
        mode: ScanMode,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._folders = folders
        self._recursive = recursive
        self._mode = mode
        self._abort = False

    def abort(self) -> None:
        """Request cancellation of the current scan."""
        self._abort = True

    def run(self) -> None:
        try:
            files = self._collect_files()
            if self._abort:
                return
            groups = self._detect_duplicates(files)
            if not self._abort:
                self.finished.emit(groups)
        except Exception as exc:
            self.error.emit(str(exc))

    def _collect_files(self) -> list[FileEntry]:
        """Collect all files from the selected folders."""
        entries: list[FileEntry] = []
        for folder in self._folders:
            if not folder.is_dir():
                continue
            pattern = "**/*" if self._recursive else "*"
            for path in folder.glob(pattern):
                if self._abort:
                    return entries
                if path.is_file():
                    try:
                        stat = path.stat()
                        entry = FileEntry(
                            path=path,
                            size=stat.st_size,
                            modified=stat.st_mtime,
                        )
                        entries.append(entry)
                        self.file_scanned.emit(path.name)
                    except (OSError, PermissionError):
                        continue
        return entries

    def _detect_duplicates(self, files: list[FileEntry]) -> list[list[FileEntry]]:
        """Group files by duplicate criteria according to scan mode."""
        total = len(files)

        if self._mode != ScanMode.EITHER:
            groups: dict[str, list[FileEntry]] = defaultdict(list)
            for idx, entry in enumerate(files):
                if self._abort:
                    return []
                key = self._compute_key(entry)
                if key:
                    entry.group_key = key
                    groups[key].append(entry)
                self.progress.emit(idx + 1, total)
            return [g for g in groups.values() if len(g) > 1]

        # EITHER : regroupe par hash OU par nom — union des groupes
        hash_groups: dict[str, list[FileEntry]] = defaultdict(list)
        name_groups: dict[str, list[FileEntry]] = defaultdict(list)

        for idx, entry in enumerate(files):
            if self._abort:
                return []
            file_hash = self._hash_file(entry.path)
            if file_hash:
                hash_groups[file_hash].append(entry)
            name_groups[entry.name.lower()].append(entry)
            self.progress.emit(idx + 1, total)

        seen: set[str] = set()
        result: list[list[FileEntry]] = []

        for groups_dict in (hash_groups, name_groups):
            for group in groups_dict.values():
                if len(group) < 2:
                    continue
                key = frozenset(str(e.path) for e in group)
                frozen_key = str(sorted(key))
                if frozen_key not in seen:
                    seen.add(frozen_key)
                    result.append(group)

        return result

    def _compute_key(self, entry: FileEntry) -> Optional[str]:
        """Compute the grouping key for a file based on scan mode."""
        if self._mode == ScanMode.NAME:
            return entry.name.lower()
        if self._mode == ScanMode.HASH:
            return self._hash_file(entry.path)
        if self._mode == ScanMode.BOTH:
            file_hash = self._hash_file(entry.path)
            if file_hash is None:
                return None
            return f"{entry.name.lower()}::{file_hash}"
        if self._mode == ScanMode.EITHER:
            file_hash = self._hash_file(entry.path)
            return file_hash if file_hash else entry.name.lower()
        return None

    def _hash_file(self, path: Path) -> Optional[str]:
        """Compute SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                while chunk := f.read(HASH_CHUNK_SIZE):
                    if self._abort:
                        return None
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, PermissionError):
            return None
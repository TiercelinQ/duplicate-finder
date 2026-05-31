from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QObject, pyqtSlot

from config import ScanMode, SCAN_SECTION, RESULTS_SECTION
from models.scanner import ScanWorker
from models.preferences import Preferences
from utils.helpers import format_size


class ScanController(QObject):
    """Connects ScanView ↔ ScanWorker. Manages folder selection and scan lifecycle."""

    def __init__(self, main_window, preferences: Preferences, parent=None) -> None:
        super().__init__(parent)
        self._win = main_window
        self._prefs = preferences
        self._worker: ScanWorker | None = None

        self._connect_signals()
        self._restore_preferences()

    def _connect_signals(self) -> None:
        view = self._win.scan_view
        view.folder_add_requested.connect(self._on_folder_add)
        view.folder_remove_requested.connect(self._on_folder_remove)
        view.scan_requested.connect(self._on_scan_requested)

    def _restore_preferences(self) -> None:
        view = self._win.scan_view
        for folder in self._prefs.last_folders:
            view.add_folder(folder)
        view.set_recursive(self._prefs.scan_recursive)
        try:
            mode = ScanMode[self._prefs.scan_mode]
        except KeyError:
            mode = ScanMode.HASH
        view.set_scan_mode(mode)

    @pyqtSlot()
    def _on_folder_add(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self._win,
            "Sélectionner un dossier",
            str(Path.home()),
        )
        if folder:
            self._win.scan_view.add_folder(folder)
            self._save_folder_prefs()

    @pyqtSlot(list)
    def _on_folder_remove(self, paths: list[str]) -> None:
        self._win.scan_view.remove_folders(paths)
        self._save_folder_prefs()

    @pyqtSlot(list, bool, object)
    def _on_scan_requested(self, folders: list[Path], recursive: bool, mode: ScanMode) -> None:
        if not folders:
            return

        self._prefs.scan_recursive = recursive
        self._prefs.scan_mode = mode.name
        self._prefs.save()

        self._win.scan_view.set_scanning(True)
        self._win.statusbar_widget.set_message("Analyse en cours…")
        self._win.statusbar_widget.show_progress(0, 0)

        self._worker = ScanWorker(folders, recursive, mode)
        self._worker.progress.connect(self._on_progress)
        self._worker.file_scanned.connect(self._on_file_scanned)
        self._worker.finished.connect(self._on_scan_finished)
        self._worker.error.connect(self._on_scan_error)
        self._worker.start()

    @pyqtSlot(int, int)
    def _on_progress(self, current: int, total: int) -> None:
        self._win.statusbar_widget.show_progress(current, total)

    @pyqtSlot(str)
    def _on_file_scanned(self, filename: str) -> None:
        self._win.statusbar_widget.set_message(f"Analyse : {filename}")

    @pyqtSlot(list)
    def _on_scan_finished(self, groups: list) -> None:
        self._win.scan_view.set_scanning(False)
        self._win.statusbar_widget.hide_progress()

        total_files = sum(len(g) for g in groups)
        recoverable = sum(
            sum(e.size for e in group[1:])
            for group in groups
        )

        if groups:
            self._win.statusbar_widget.set_message(
                f"Analyse terminée — {len(groups)} groupe(s), {total_files} fichier(s) en doublon."
            )
            self._win.statusbar_widget.set_info(
                f"{total_files} doublon(s) · {format_size(recoverable)} récupérables"
            )
        else:
            self._win.statusbar_widget.set_message("Analyse terminée — aucun doublon détecté.")
            self._win.statusbar_widget.set_info("")

        self._win.results_view.populate(groups)
        self._win.sidebar.set_active(RESULTS_SECTION)
        self._win.show_section(RESULTS_SECTION)
        self._worker = None

    @pyqtSlot(str)
    def _on_scan_error(self, message: str) -> None:
        self._win.scan_view.set_scanning(False)
        self._win.statusbar_widget.hide_progress()
        self._win.statusbar_widget.set_message("Erreur lors de l'analyse.")
        QMessageBox.critical(self._win, "Erreur d'analyse", message)
        self._worker = None

    def _save_folder_prefs(self) -> None:
        view = self._win.scan_view
        folders = [
            view._folder_list.item(i).text()
            for i in range(view._folder_list.count())
        ]
        self._prefs.last_folders = folders
        self._prefs.save()

    def abort(self) -> None:
        """Abort any running scan worker."""
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait()
import csv
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog, QInputDialog, QMessageBox
)
from PyQt6.QtCore import QObject, pyqtSlot

from models.file_entry import FileEntry


try:
    from send2trash import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False


class FileController(QObject):
    """Connects ResultsView ↔ file operations: delete, rename, move, open, export."""

    def __init__(self, main_window, parent=None) -> None:
        super().__init__(parent)
        self._win = main_window
        self._connect_signals()

    def _connect_signals(self) -> None:
        view = self._win.results_view
        view.open_requested.connect(self._on_open)
        view.delete_requested.connect(self._on_delete)
        view.rename_requested.connect(self._on_rename)
        view.move_requested.connect(self._on_move)
        view.export_requested.connect(self._on_export)

    @pyqtSlot(object)
    def _on_open(self, entry: FileEntry) -> None:
        try:
            subprocess.run(["explorer", "/select,", str(entry.path)])
        except Exception as exc:
            QMessageBox.critical(
                self._win,
                "Erreur",
                f"Impossible d'ouvrir l'emplacement :\n{exc}",
            )

    @pyqtSlot(list)
    def _on_delete(self, entries: list[FileEntry]) -> None:
        if not entries:
            return

        names = "\n".join(f"  • {e.name}" for e in entries[:10])
        if len(entries) > 10:
            names += f"\n  … et {len(entries) - 10} autre(s)"

        reply = QMessageBox.question(
            self._win,
            "Confirmer la suppression",
            f"Envoyer {len(entries)} fichier(s) dans la corbeille ?\n\n{names}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        failed: list[str] = []
        deleted_paths: list[str] = []

        for entry in entries:
            path_str = str(entry.path)
            try:
                if SEND2TRASH_AVAILABLE:
                    send2trash(path_str)
                else:
                    entry.path.unlink()
                deleted_paths.append(path_str)
            except Exception as exc:
                failed.append(f"{entry.name} : {exc}")

        if deleted_paths:
            self._win.results_view.remove_entries(deleted_paths)
            self._win.statusbar_widget.set_message(
                f"{len(deleted_paths)} fichier(s) supprimé(s)."
            )

        if failed:
            QMessageBox.warning(
                self._win,
                "Erreurs de suppression",
                "Certains fichiers n'ont pas pu être supprimés :\n\n" + "\n".join(failed),
            )

    @pyqtSlot(object)
    def _on_rename(self, entry: FileEntry) -> None:
        new_name, ok = QInputDialog.getText(
            self._win,
            "Renommer le fichier",
            "Nouveau nom :",
            text=entry.name,
        )
        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()
        new_path = entry.path.parent / new_name
        old_path_str = str(entry.path)

        if new_path.exists():
            QMessageBox.warning(
                self._win,
                "Nom déjà utilisé",
                f"Un fichier nommé « {new_name} » existe déjà dans ce dossier.",
            )
            return

        try:
            entry.path.rename(new_path)
            self._win.results_view.update_entry_name(
                old_path_str, str(new_path), new_name
            )
            self._win.statusbar_widget.set_message(f"Renommé : {new_name}")
        except Exception as exc:
            QMessageBox.critical(
                self._win,
                "Erreur de renommage",
                f"Impossible de renommer le fichier :\n{exc}",
            )

    @pyqtSlot(list)
    def _on_move(self, entries: list[FileEntry]) -> None:
        if not entries:
            return

        destination = QFileDialog.getExistingDirectory(
            self._win,
            "Choisir le dossier de destination",
            str(entries[0].path.parent),
        )
        if not destination:
            return

        dest_path = Path(destination)
        failed: list[str] = []
        moved_paths: list[tuple[str, str]] = []

        for entry in entries:
            old_path_str = str(entry.path)
            new_path = dest_path / entry.name

            if new_path.exists():
                failed.append(
                    f"{entry.name} : un fichier portant ce nom existe déjà dans la destination."
                )
                continue

            try:
                entry.path.rename(new_path)
                moved_paths.append((old_path_str, str(new_path)))
            except Exception as exc:
                failed.append(f"{entry.name} : {exc}")

        for old_path_str, new_path_str in moved_paths:
            self._win.results_view.update_entry_path(old_path_str, new_path_str)

        if moved_paths:
            self._win.statusbar_widget.set_message(
                f"{len(moved_paths)} fichier(s) déplacé(s) vers {destination}"
            )

        if failed:
            QMessageBox.warning(
                self._win,
                "Erreurs de déplacement",
                "Certains fichiers n'ont pas pu être déplacés :\n\n" + "\n".join(failed),
            )

    @pyqtSlot()
    def _on_export(self) -> None:
        groups = self._win.results_view.get_all_groups()
        if not groups:
            return

        path, _ = QFileDialog.getSaveFileName(
            self._win,
            "Exporter les résultats",
            str(Path.home() / "doublons.csv"),
            "Fichiers CSV (*.csv)",
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Groupe", "Nom", "Taille (octets)", "Modifié", "Chemin"])
                for idx, group in enumerate(groups, start=1):
                    for entry in group:
                        writer.writerow([
                            idx,
                            entry.name,
                            entry.size,
                            entry.modified_display,
                            entry.path_display,
                        ])
            self._win.statusbar_widget.set_message(f"Export CSV : {path}")
        except Exception as exc:
            QMessageBox.critical(
                self._win,
                "Erreur d'export",
                f"Impossible d'exporter les résultats :\n{exc}",
            )
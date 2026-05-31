from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QButtonGroup,
    QRadioButton, QGroupBox, QSizePolicy, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt

from config import ScanMode


class ScanView(QWidget):
    """View for folder selection and scan configuration."""

    scan_requested = pyqtSignal(list, bool, object)
    folder_add_requested = pyqtSignal()
    folder_remove_requested = pyqtSignal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ScanView")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(24)

        self._build_header()
        self._build_folder_section()
        self._build_options_section()
        self._build_actions()
        self._layout.addStretch()

    def _build_header(self) -> None:
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        title = QLabel("Analyse")
        title.setObjectName("SectionTitle")

        subtitle = QLabel("Sélectionnez un ou plusieurs dossiers et configurez l'analyse.")
        subtitle.setObjectName("SectionSubtitle")
        subtitle.setWordWrap(True)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self._layout.addWidget(header)

    def _build_folder_section(self) -> None:
        group = QGroupBox("Dossiers à analyser")
        group.setObjectName("ScanGroupBox")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)

        self._folder_list = QListWidget()
        self._folder_list.setObjectName("FolderList")
        self._folder_list.setMinimumHeight(120)
        self._folder_list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )
        self._folder_list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        btn_row = QHBoxLayout()
        self._btn_add = QPushButton("Ajouter un dossier")
        self._btn_add.setObjectName("BtnSecondary")
        self._btn_remove = QPushButton("Retirer")
        self._btn_remove.setObjectName("BtnSecondary")
        self._btn_remove.setEnabled(False)

        btn_row.addWidget(self._btn_add)
        btn_row.addWidget(self._btn_remove)
        btn_row.addStretch()

        group_layout.addWidget(self._folder_list)
        group_layout.addLayout(btn_row)
        self._layout.addWidget(group)

        self._btn_add.clicked.connect(self.folder_add_requested)
        self._btn_remove.clicked.connect(self._on_remove_clicked)
        self._folder_list.itemSelectionChanged.connect(self._on_selection_changed)

    def _build_options_section(self) -> None:
        group = QGroupBox("Options")
        group.setObjectName("ScanGroupBox")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)

        self._recursive_check = QCheckBox("Inclure les sous-dossiers (récursif)")
        self._recursive_check.setObjectName("ScanCheckBox")
        self._recursive_check.setChecked(True)

        mode_label = QLabel("Méthode de détection des doublons :")
        mode_label.setObjectName("OptionLabel")

        self._mode_group = QButtonGroup(self)
        modes = [
            (ScanMode.HASH, "Par contenu (hash SHA-256)"),
            (ScanMode.NAME, "Par nom de fichier"),
            (ScanMode.BOTH, "Par contenu ET nom"),
            (ScanMode.EITHER, "Par contenu OU nom"),
        ]
        self._mode_radios: dict[ScanMode, QRadioButton] = {}
        for mode, label in modes:
            radio = QRadioButton(label)
            radio.setObjectName("ScanRadio")
            self._mode_group.addButton(radio)
            self._mode_radios[mode] = radio

        self._mode_radios[ScanMode.HASH].setChecked(True)

        group_layout.addWidget(self._recursive_check)
        group_layout.addWidget(mode_label)
        for radio in self._mode_radios.values():
            group_layout.addWidget(radio)

        self._layout.addWidget(group)

    def _build_actions(self) -> None:
        row = QHBoxLayout()
        row.addStretch()

        self._btn_scan = QPushButton("Lancer l'analyse")
        self._btn_scan.setObjectName("BtnPrimary")
        self._btn_scan.setMinimumHeight(36)
        self._btn_scan.setEnabled(False)

        row.addWidget(self._btn_scan)
        self._layout.addLayout(row)
        self._btn_scan.clicked.connect(self._on_scan_clicked)

    def _on_scan_clicked(self) -> None:
        folders = [
            Path(self._folder_list.item(i).text())
            for i in range(self._folder_list.count())
        ]
        recursive = self._recursive_check.isChecked()
        mode = next(
            mode for mode, radio in self._mode_radios.items() if radio.isChecked()
        )
        self.scan_requested.emit(folders, recursive, mode)

    def _on_remove_clicked(self) -> None:
        selected = [item.text() for item in self._folder_list.selectedItems()]
        self.folder_remove_requested.emit(selected)

    def _on_selection_changed(self) -> None:
        has_selection = bool(self._folder_list.selectedItems())
        self._btn_remove.setEnabled(has_selection)

    def add_folder(self, path: str) -> None:
        existing = [
            self._folder_list.item(i).text()
            for i in range(self._folder_list.count())
        ]
        if path not in existing:
            self._folder_list.addItem(QListWidgetItem(path))
            self._btn_scan.setEnabled(True)

    def remove_folders(self, paths: list[str]) -> None:
        for i in range(self._folder_list.count() - 1, -1, -1):
            if self._folder_list.item(i).text() in paths:
                self._folder_list.takeItem(i)
        self._btn_scan.setEnabled(self._folder_list.count() > 0)

    def set_recursive(self, value: bool) -> None:
        self._recursive_check.setChecked(value)

    def set_scan_mode(self, mode: ScanMode) -> None:
        if mode in self._mode_radios:
            self._mode_radios[mode].setChecked(True)

    def set_scanning(self, scanning: bool) -> None:
        self._btn_scan.setEnabled(not scanning)
        self._btn_add.setEnabled(not scanning)
        self._btn_remove.setEnabled(not scanning)
        self._btn_scan.setText("Analyse en cours…" if scanning else "Lancer l'analyse")
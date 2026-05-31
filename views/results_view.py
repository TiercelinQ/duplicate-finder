from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QSizePolicy,
    QAbstractItemView, QLineEdit, QMenu
)
from PyQt6.QtCore import pyqtSignal, Qt, QSortFilterProxyModel
from PyQt6.QtGui import QAction, QClipboard, QGuiApplication

from models.file_entry import FileEntry


class ResultsView(QWidget):
    """View for displaying duplicate groups and file actions."""

    delete_requested = pyqtSignal(list)
    rename_requested = pyqtSignal(object)
    move_requested = pyqtSignal(list)
    open_requested = pyqtSignal(object)
    export_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ResultsView")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(16)

        self._file_map: dict[str, FileEntry] = {}
        self._all_groups: list[list[FileEntry]] = []

        self._build_header()
        self._build_search()
        self._build_toolbar()
        self._build_tree()
        self._build_actions()

    def _build_header(self) -> None:
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        self._title = QLabel("Résultats")
        self._title.setObjectName("SectionTitle")

        self._subtitle = QLabel("Aucune analyse effectuée.")
        self._subtitle.setObjectName("SectionSubtitle")
        self._subtitle.setWordWrap(True)

        header_layout.addWidget(self._title)
        header_layout.addWidget(self._subtitle)
        self._layout.addWidget(header)

    def _build_search(self) -> None:
        self._search_input = QLineEdit()
        self._search_input.setObjectName("SearchInput")
        self._search_input.setPlaceholderText("Filtrer par nom ou chemin…")
        self._search_input.setMinimumHeight(36)
        self._search_input.setClearButtonEnabled(True)
        self._search_input.textChanged.connect(self._on_filter_changed)
        self._layout.addWidget(self._search_input)

    def _build_toolbar(self) -> None:
        row = QHBoxLayout()

        self._btn_select_all = QPushButton("Tout sélectionner")
        self._btn_select_all.setObjectName("BtnSecondary")
        self._btn_deselect_all = QPushButton("Tout désélectionner")
        self._btn_deselect_all.setObjectName("BtnSecondary")

        row.addWidget(self._btn_select_all)
        row.addWidget(self._btn_deselect_all)
        row.addStretch()

        self._layout.addLayout(row)

        self._btn_select_all.clicked.connect(self._select_all)
        self._btn_deselect_all.clicked.connect(self._deselect_all)

    def _build_tree(self) -> None:
        self._tree = QTreeWidget()
        self._tree.setObjectName("ResultsTree")
        self._tree.setColumnCount(4)
        self._tree.setHeaderLabels(["Nom", "Taille", "Modifié", "Chemin"])
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._tree.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._tree.setAlternatingRowColors(False)
        self._tree.setRootIsDecorated(True)
        self._tree.setSortingEnabled(True)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)

        header = self._tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(False)
        header.setSortIndicatorShown(True)

        self._tree.itemSelectionChanged.connect(self._on_selection_changed)
        self._layout.addWidget(self._tree)

    def _build_actions(self) -> None:
        row = QHBoxLayout()

        self._btn_export = QPushButton("Exporter CSV")
        self._btn_export.setObjectName("BtnSecondary")
        self._btn_export.setEnabled(False)

        row.addWidget(self._btn_export)
        row.addStretch()

        self._btn_open = QPushButton("Ouvrir l'emplacement")
        self._btn_open.setObjectName("BtnSecondary")
        self._btn_open.setEnabled(False)

        self._btn_copy_path = QPushButton("Copier le chemin")
        self._btn_copy_path.setObjectName("BtnSecondary")
        self._btn_copy_path.setEnabled(False)

        self._btn_move = QPushButton("Déplacer")
        self._btn_move.setObjectName("BtnSecondary")
        self._btn_move.setEnabled(False)

        self._btn_rename = QPushButton("Renommer")
        self._btn_rename.setObjectName("BtnSecondary")
        self._btn_rename.setEnabled(False)

        self._btn_delete = QPushButton("Supprimer")
        self._btn_delete.setObjectName("BtnDanger")
        self._btn_delete.setEnabled(False)

        row.addWidget(self._btn_open)
        row.addWidget(self._btn_copy_path)
        row.addWidget(self._btn_move)
        row.addWidget(self._btn_rename)
        row.addWidget(self._btn_delete)
        self._layout.addLayout(row)

        self._btn_export.clicked.connect(self.export_requested)
        self._btn_open.clicked.connect(self._on_open_clicked)
        self._btn_copy_path.clicked.connect(self._on_copy_path_clicked)
        self._btn_delete.clicked.connect(self._on_delete_clicked)
        self._btn_rename.clicked.connect(self._on_rename_clicked)
        self._btn_move.clicked.connect(self._on_move_clicked)

    def populate(self, groups: list[list[FileEntry]]) -> None:
        """Populate the tree with duplicate groups."""
        self._all_groups = groups
        self._search_input.clear()
        self._render_groups(groups)

    def _render_groups(self, groups: list[list[FileEntry]]) -> None:
        """Render a (filtered) list of groups into the tree."""
        self._tree.clear()
        self._file_map.clear()

        total_files = sum(len(g) for g in self._all_groups)
        visible_files = sum(len(g) for g in groups)

        if not self._all_groups:
            self._subtitle.setText("Aucun doublon détecté.")
        elif len(groups) != len(self._all_groups):
            self._subtitle.setText(
                f"{len(groups)} groupe(s) affichés sur {len(self._all_groups)} "
                f"— {visible_files}/{total_files} fichiers."
            )
        else:
            self._subtitle.setText(
                f"{len(self._all_groups)} groupe(s) de doublons "
                f"— {total_files} fichiers concernés."
            )

        for idx, group in enumerate(groups, start=1):
            group_item = QTreeWidgetItem(self._tree)
            group_item.setText(0, f"Groupe {idx} — {len(group)} fichiers")
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = group_item.font(0)
            font.setBold(True)
            for col in range(self._tree.columnCount()):
                group_item.setFont(col, font)

            for entry in group:
                file_item = QTreeWidgetItem(group_item)
                file_item.setText(0, entry.name)
                file_item.setText(1, entry.size_display)
                file_item.setText(2, entry.modified_display)
                file_item.setText(3, entry.path_display)
                file_item.setData(0, Qt.ItemDataRole.UserRole, entry.path_display)
                self._file_map[entry.path_display] = entry

        self._tree.expandAll()
        self._btn_export.setEnabled(bool(self._all_groups))

    def _on_filter_changed(self, text: str) -> None:
        """Filter visible groups by name or path."""
        query = text.strip().lower()
        if not query:
            self._render_groups(self._all_groups)
            return

        filtered: list[list[FileEntry]] = []
        for group in self._all_groups:
            matched = [
                e for e in group
                if query in e.name.lower() or query in e.path_display.lower()
            ]
            if len(matched) >= 1:
                filtered.append(matched)

        self._render_groups(filtered)

    def _on_context_menu(self, position) -> None:
        """Show right-click context menu on file items."""
        item = self._tree.itemAt(position)
        if not item:
            return
        path_str = item.data(0, Qt.ItemDataRole.UserRole)
        if not path_str:
            return

        menu = QMenu(self)
        action_copy = QAction("Copier le chemin", self)
        action_copy.triggered.connect(lambda: self._copy_path(path_str))
        menu.addAction(action_copy)
        menu.exec(self._tree.viewport().mapToGlobal(position))

    def _copy_path(self, path: str) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(path)

    def _get_selected_entries(self) -> list[FileEntry]:
        entries = []
        for item in self._tree.selectedItems():
            path_str = item.data(0, Qt.ItemDataRole.UserRole)
            if path_str and path_str in self._file_map:
                entries.append(self._file_map[path_str])
        return entries

    def _on_selection_changed(self) -> None:
        selected = self._get_selected_entries()
        has_one = len(selected) == 1
        has_any = len(selected) >= 1

        self._btn_open.setEnabled(has_one)
        self._btn_copy_path.setEnabled(has_one)
        self._btn_delete.setEnabled(has_any)
        self._btn_rename.setEnabled(has_one)
        self._btn_move.setEnabled(has_any)

    def _on_delete_clicked(self) -> None:
        self.delete_requested.emit(self._get_selected_entries())

    def _on_rename_clicked(self) -> None:
        selected = self._get_selected_entries()
        if selected:
            self.rename_requested.emit(selected[0])

    def _on_move_clicked(self) -> None:
        self.move_requested.emit(self._get_selected_entries())

    def _on_open_clicked(self) -> None:
        selected = self._get_selected_entries()
        if selected:
            self.open_requested.emit(selected[0])

    def _on_copy_path_clicked(self) -> None:
        selected = self._get_selected_entries()
        if selected:
            self._copy_path(selected[0].path_display)

    def _select_all(self) -> None:
        for i in range(self._tree.topLevelItemCount()):
            group = self._tree.topLevelItem(i)
            for j in range(group.childCount()):
                group.child(j).setSelected(True)

    def _deselect_all(self) -> None:
        self._tree.clearSelection()

    def remove_entries(self, paths: list[str]) -> None:
        """Remove file entries from the tree after deletion/move."""
        for path in paths:
            self._file_map.pop(path, None)
            self._all_groups = [
                [e for e in group if str(e.path) != path]
                for group in self._all_groups
            ]
        self._all_groups = [g for g in self._all_groups if len(g) >= 2]

        for i in range(self._tree.topLevelItemCount() - 1, -1, -1):
            group = self._tree.topLevelItem(i)
            for j in range(group.childCount() - 1, -1, -1):
                child = group.child(j)
                if child.data(0, Qt.ItemDataRole.UserRole) in paths:
                    group.removeChild(child)
            if group.childCount() < 2:
                self._tree.takeTopLevelItem(i)

        self._btn_export.setEnabled(bool(self._all_groups))

    def update_entry_name(self, old_path: str, new_path: str, new_name: str) -> None:
        """Update a renamed entry in the tree."""
        entry = self._file_map.pop(old_path, None)
        if entry:
            entry.path = Path(new_path)
            entry.name = new_name
            self._file_map[new_path] = entry

        for i in range(self._tree.topLevelItemCount()):
            group = self._tree.topLevelItem(i)
            for j in range(group.childCount()):
                child = group.child(j)
                if child.data(0, Qt.ItemDataRole.UserRole) == old_path:
                    child.setText(0, new_name)
                    child.setText(3, new_path)
                    child.setData(0, Qt.ItemDataRole.UserRole, new_path)
                    return

    def update_entry_path(self, old_path: str, new_path: str) -> None:
        """Update a moved entry in the tree."""
        entry = self._file_map.pop(old_path, None)
        if entry:
            entry.path = Path(new_path)
            self._file_map[new_path] = entry

        for i in range(self._tree.topLevelItemCount()):
            group = self._tree.topLevelItem(i)
            for j in range(group.childCount()):
                child = group.child(j)
                if child.data(0, Qt.ItemDataRole.UserRole) == old_path:
                    child.setText(3, new_path)
                    child.setData(0, Qt.ItemDataRole.UserRole, new_path)
                    return

    def get_all_groups(self) -> list[list[FileEntry]]:
        return self._all_groups
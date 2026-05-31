from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal

from config import SCAN_SECTION, RESULTS_SECTION


SECTIONS = [
    (SCAN_SECTION, "Analyse", "🔍"),
    (RESULTS_SECTION, "Résultats", "📋"),
]


class SidebarItem(QPushButton):
    """A single navigation item in the sidebar."""

    def __init__(self, section_id: str, label: str, icon: str, parent=None) -> None:
        super().__init__(parent)
        self.section_id = section_id
        self.setText(f"  {icon}  {label}")
        self.setObjectName("SidebarItem")
        self.setCheckable(True)
        self.setMinimumHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setToolTip(label)


class Sidebar(QWidget):
    """Fixed sidebar with section navigation."""

    section_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 8, 0, 8)
        self._layout.setSpacing(0)

        self._items: dict[str, SidebarItem] = {}
        self._active_section: str = ""

        self._build_items()

    def _build_items(self) -> None:
        for section_id, label, icon in SECTIONS:
            item = SidebarItem(section_id, label, icon)
            item.clicked.connect(lambda checked, sid=section_id: self._on_item_clicked(sid))
            self._items[section_id] = item
            self._layout.addWidget(item)
        self._layout.addStretch()

    def _on_item_clicked(self, section_id: str) -> None:
        self.set_active(section_id)
        self.section_changed.emit(section_id)

    def set_active(self, section_id: str) -> None:
        """Highlight the active section item."""
        for sid, item in self._items.items():
            item.setChecked(sid == section_id)
        self._active_section = section_id

    @property
    def active_section(self) -> str:
        return self._active_section
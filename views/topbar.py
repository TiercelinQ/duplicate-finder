from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from config import APP_NAME, TOPBAR_HEIGHT


class Topbar(QWidget):
    """Application topbar: logo, contextual actions, theme toggle."""

    theme_toggled = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Topbar")
        self.setFixedHeight(TOPBAR_HEIGHT)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 0, 16, 0)
        self._layout.setSpacing(8)

        self._logo_label = QLabel(APP_NAME)
        self._logo_label.setObjectName("TopbarLogo")
        font = QFont()
        font.setWeight(QFont.Weight.DemiBold)
        self._logo_label.setFont(font)

        self._contextual_layout = QHBoxLayout()
        self._contextual_layout.setSpacing(8)
        self._contextual_widget = QWidget()
        self._contextual_widget.setLayout(self._contextual_layout)
        self._contextual_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("ThemeToggleButton")
        self._theme_btn.setToolTip("Passer en mode sombre / clair")
        self._theme_btn.setFixedSize(40, 40)
        self._theme_btn.clicked.connect(self.theme_toggled)

        self._layout.addWidget(self._logo_label)
        self._layout.addWidget(self._contextual_widget)
        self._layout.addWidget(self._theme_btn)

    def set_contextual_actions(self, actions: list[QPushButton]) -> None:
        """Replace contextual action buttons in the center zone."""
        while self._contextual_layout.count():
            item = self._contextual_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        for btn in actions[:4]:
            btn.setObjectName("TopbarAction")
            self._contextual_layout.addWidget(btn)
        self._contextual_layout.addStretch()

    def update_theme_icon(self, is_dark: bool) -> None:
        """Update theme button label according to current theme."""
        self._theme_btn.setText("☀" if is_dark else "☾")
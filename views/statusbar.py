from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar, QSizePolicy
from PyQt6.QtCore import Qt

from config import STATUSBAR_HEIGHT


class Statusbar(QWidget):
    """Application statusbar: status message, progress, contextual info."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Statusbar")
        self.setFixedHeight(STATUSBAR_HEIGHT)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 0, 16, 0)
        self._layout.setSpacing(8)

        self._status_label = QLabel("Prêt")
        self._status_label.setObjectName("StatusbarMessage")
        self._status_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        self._progress = QProgressBar()
        self._progress.setObjectName("StatusbarProgress")
        self._progress.setFixedHeight(8)
        self._progress.setMinimumWidth(120)
        self._progress.setMaximumWidth(200)
        self._progress.setTextVisible(False)
        self._progress.hide()

        self._info_label = QLabel()
        self._info_label.setObjectName("StatusbarInfo")
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._layout.addWidget(self._status_label)
        self._layout.addWidget(self._progress)
        self._layout.addWidget(self._info_label)

    def set_message(self, message: str) -> None:
        self._status_label.setText(message)

    def set_info(self, info: str) -> None:
        self._info_label.setText(info)

    def show_progress(self, value: int, maximum: int) -> None:
        self._progress.setMaximum(maximum)
        self._progress.setValue(value)
        self._progress.show()

    def hide_progress(self) -> None:
        self._progress.hide()
        self._progress.setValue(0)
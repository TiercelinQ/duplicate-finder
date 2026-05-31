from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize

from config import (
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    SCAN_SECTION, RESULTS_SECTION, SETTINGS_SECTION,
    APP_NAME
)
from views.topbar import Topbar
from views.sidebar import Sidebar
from views.statusbar import Statusbar
from views.scan_view import ScanView
from views.results_view import ResultsView


class MainWindow(QMainWindow):
    """Main application window assembling all layout components."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.topbar = Topbar()
        root_layout.addWidget(self.topbar)

        separator_top = QFrame()
        separator_top.setObjectName("TopbarSeparator")
        separator_top.setFrameShape(QFrame.Shape.HLine)
        separator_top.setFixedHeight(1)
        root_layout.addWidget(separator_top)

        body = QWidget()
        body.setObjectName("Body")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.sidebar = Sidebar()
        body_layout.addWidget(self.sidebar, stretch=1)

        separator_side = QFrame()
        separator_side.setObjectName("SidebarSeparator")
        separator_side.setFrameShape(QFrame.Shape.VLine)
        separator_side.setFixedWidth(1)
        body_layout.addWidget(separator_side)

        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentStack")
        self.stack.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.scan_view = ScanView()
        self.results_view = ResultsView()

        self.stack.addWidget(self.scan_view)
        self.stack.addWidget(self.results_view)

        body_layout.addWidget(self.stack, stretch=5)
        root_layout.addWidget(body)

        separator_bottom = QFrame()
        separator_bottom.setObjectName("StatusbarSeparator")
        separator_bottom.setFrameShape(QFrame.Shape.HLine)
        separator_bottom.setFixedHeight(1)
        root_layout.addWidget(separator_bottom)

        self.statusbar_widget = Statusbar()
        root_layout.addWidget(self.statusbar_widget)

    def show_section(self, section_id: str) -> None:
        """Switch the visible content view."""
        mapping = {
            SCAN_SECTION: self.scan_view,
            RESULTS_SECTION: self.results_view,
        }
        widget = mapping.get(section_id)
        if widget:
            self.stack.setCurrentWidget(widget)

    def restore_geometry_from_prefs(self, prefs: dict) -> None:
        """Restore window size and position from saved preferences."""
        width = prefs.get("width", 1280)
        height = prefs.get("height", 800)
        x = prefs.get("x")
        y = prefs.get("y")
        self.resize(width, height)
        if x is not None and y is not None:
            self.move(x, y)
        else:
            self._center_on_screen()

    def _center_on_screen(self) -> None:
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def closeEvent(self, event) -> None:
        self.geometry_save_requested = True
        super().closeEvent(event)